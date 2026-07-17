"""Gerenciador de IA (AIManager) — orquestra os provedores com failover.

É o único ponto de entrada para o resto do sistema pedir uma resposta de IA.
Responsabilidades (conforme o documento do projeto):
  * Enviar a pergunta ao modelo principal.
  * Em caso de erro/indisponibilidade, alternar automaticamente para o
    próximo modelo da lista (failover).
  * Registrar qual modelo respondeu (para o painel administrativo).
  * Nunca informar o cliente sobre a troca — o atendimento não pode parar.
"""

from __future__ import annotations

from app.ai.base import AIProvider
from app.ai.providers.claude_provider import ClaudeProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.schemas import AIMessage, AIResponse
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
}


class AIManager:
    """Seleciona e executa provedores de IA na ordem configurada."""

    def __init__(self) -> None:
        # Instancia os provedores na ordem definida em AI_PROVIDER_ORDER.
        self._providers: list[AIProvider] = []
        for provider_name in settings.provider_order:
            provider_cls = _PROVIDER_REGISTRY.get(provider_name)
            if provider_cls is None:
                logger.warning("Provedor desconhecido ignorado: %s", provider_name)
                continue
            self._providers.append(provider_cls())

    async def generate(
        self,
        messages: list[AIMessage],
        *,
        system: str | None = None,
        max_tokens: int | None = None,
    ) -> AIResponse:
        """Tenta cada provedor em ordem até um responder com sucesso.

        Raises:
            AllProvidersFailedError: se nenhum provedor conseguir responder.
        """
        tokens = max_tokens or settings.ai_max_tokens
        last_error: Exception | None = None

        for provider in self._providers:
            if not provider.is_available():
                logger.info("Provedor %s indisponível — pulando.", provider.name)
                continue
            try:
                logger.info("Tentando provedor: %s", provider.name)
                response = await provider.generate(
                    messages, system=system, max_tokens=tokens
                )
                logger.info(
                    "Resposta de %s (%s) — tokens in/out: %d/%d",
                    response.provider,
                    response.model,
                    response.input_tokens,
                    response.output_tokens,
                )
                return response
            except AIProviderError as exc:
                # Registra o erro e segue para o próximo provedor (failover).
                last_error = exc
                logger.warning("Failover: %s falhou, tentando o próximo.", provider.name)

        raise AllProvidersFailedError(
            f"Todos os provedores de IA falharam. Último erro: {last_error}"
        )


# Instância única compartilhada por toda a aplicação.
ai_manager = AIManager()
