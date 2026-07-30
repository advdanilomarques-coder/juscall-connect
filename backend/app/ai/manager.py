"""Gerenciador de IA (AIManager) — orquestra os provedores.

É o ÚNICO ponto de entrada para o resto do sistema pedir uma resposta de IA.
Responsabilidades (conforme o documento do projeto):
  * Roteamento inteligente: escolhe o provedor conforme o tipo de tarefa.
  * Retry com backoff exponencial em cada provedor.
  * Failover: se um provedor falhar, alterna automaticamente para o próximo.
  * Controle de custos: calcula tokens/valor/latência de cada resposta.
  * Registrar qual modelo respondeu (para o painel administrativo).
  * Nunca informar o cliente sobre a troca — o atendimento não pode parar.

A camada de IA é totalmente desacoplada do CRM e da lógica jurídica: ela não
sabe o que é um "lead" ou um "contrato". Recebe mensagens padronizadas e
devolve uma resposta padronizada.
"""

from __future__ import annotations

import asyncio
import time

from app.ai.base import AIProvider
from app.ai.pricing import estimate_cost
from app.ai.providers.claude_provider import ClaudeProvider
from app.ai.providers.deepseek_provider import DeepSeekProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.grok_provider import GrokProvider
from app.ai.providers.mistral_provider import MistralProvider
from app.ai.providers.ollama_provider import OllamaProvider
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.providers.openrouter_provider import OpenRouterProvider
from app.ai.schemas import AIMessage, AIResponse, TaskType
from app.core.config import settings
from app.core.exceptions import AIProviderError, AllProvidersFailedError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Registro de provedores conhecidos. Para adicionar um modelo novo, basta
# implementar um Provider e registrá-lo aqui (mais o nome no AI_PROVIDER_ORDER).
_PROVIDER_REGISTRY: dict[str, type[AIProvider]] = {
    "claude": ClaudeProvider,
    "gemini": GeminiProvider,
    "openai": OpenAIProvider,
    "deepseek": DeepSeekProvider,
    "mistral": MistralProvider,
    "openrouter": OpenRouterProvider,
    "grok": GrokProvider,
    "ollama": OllamaProvider,
}


class AIManager:
    """Seleciona e executa provedores de IA com roteamento, retry e failover."""

    def __init__(self) -> None:
        # Instancia UMA vez cada provedor da ordem configurada, mantendo um
        # dicionário por nome para o roteamento inteligente por tarefa.
        self._providers: list[AIProvider] = []
        self._by_name: dict[str, AIProvider] = {}
        for provider_name in settings.provider_order:
            provider_cls = _PROVIDER_REGISTRY.get(provider_name)
            if provider_cls is None:
                logger.warning("Provedor desconhecido ignorado: %s", provider_name)
                continue
            provider = provider_cls()
            self._providers.append(provider)
            self._by_name[provider_name] = provider

        self._task_routing = settings.task_routing

    def _ordered_for_task(self, task: TaskType | None) -> list[AIProvider]:
        """Monta a ordem de tentativa: provedor preferido da tarefa primeiro.

        Se a tarefa tem um provedor mapeado em AI_TASK_ROUTING e ele existe,
        ele vai para o topo; os demais seguem como reserva (failover). Isso
        implementa o GERENCIAMENTO INTELIGENTE sem quebrar o failover.
        """
        if task is None:
            return self._providers
        preferred_name = self._task_routing.get(task.value)
        preferred = self._by_name.get(preferred_name) if preferred_name else None
        if preferred is None:
            return self._providers
        return [preferred] + [p for p in self._providers if p is not preferred]

    async def _try_provider(
        self,
        provider: AIProvider,
        messages: list[AIMessage],
        *,
        system: str | None,
        max_tokens: int,
    ) -> AIResponse:
        """Chama um provedor com retry + backoff exponencial.

        Repete até `AI_MAX_RETRIES` vezes antes de desistir e deixar o
        failover seguir para o próximo provedor.
        """
        attempts = max(1, settings.ai_max_retries)
        last_error: Exception | None = None
        for attempt in range(1, attempts + 1):
            start = time.monotonic()
            try:
                response = await provider.generate(
                    messages, system=system, max_tokens=max_tokens
                )
            except AIProviderError as exc:
                last_error = exc
                if attempt < attempts:
                    backoff = settings.ai_retry_backoff * (2 ** (attempt - 1))
                    logger.info(
                        "%s falhou (tentativa %d/%d). Novo retry em %.1fs.",
                        provider.name, attempt, attempts, backoff,
                    )
                    await asyncio.sleep(backoff)
                continue
            # Sucesso: enriquece a resposta com custo e latência.
            response.latency_ms = int((time.monotonic() - start) * 1000)
            response.cost_usd = estimate_cost(
                response.model, response.input_tokens, response.output_tokens
            )
            return response
        # Esgotou as tentativas neste provedor.
        raise last_error or AIProviderError(f"{provider.name}: falha desconhecida.")

    async def generate(
        self,
        messages: list[AIMessage],
        *,
        system: str | None = None,
        max_tokens: int | None = None,
        task: TaskType | None = None,
    ) -> AIResponse:
        """Tenta cada provedor (na ordem da tarefa) até um responder.

        Args:
            messages: histórico da conversa padronizado.
            system: instrução de sistema (personalidade/regras).
            max_tokens: limite de tokens (padrão: AI_MAX_TOKENS).
            task: tipo de tarefa para roteamento inteligente (opcional).

        Raises:
            AllProvidersFailedError: se nenhum provedor conseguir responder.
        """
        tokens = max_tokens or settings.ai_max_tokens
        last_error: Exception | None = None

        for provider in self._ordered_for_task(task):
            if not provider.is_available():
                logger.info("Provedor %s indisponível — pulando.", provider.name)
                continue
            try:
                logger.info("Tentando provedor: %s (tarefa=%s)", provider.name, task)
                response = await self._try_provider(
                    provider, messages, system=system, max_tokens=tokens
                )
                logger.info(
                    "Resposta de %s (%s) — tokens in/out: %d/%d | custo ~US$%.5f | %dms",
                    response.provider, response.model,
                    response.input_tokens, response.output_tokens,
                    response.cost_usd, response.latency_ms,
                )
                return response
            except AIProviderError as exc:
                last_error = exc
                logger.warning(
                    "Failover: %s falhou, tentando o próximo.", provider.name
                )

        raise AllProvidersFailedError(
            f"Todos os provedores de IA falharam. Último erro: {last_error}"
        )

    @property
    def available_providers(self) -> list[str]:
        """Nomes dos provedores atualmente disponíveis (para o painel admin)."""
        return [p.name for p in self._providers if p.is_available()]


# Instância única compartilhada por toda a aplicação.
ai_manager = AIManager()
