"""Interface abstrata que todo provedor de IA deve implementar.

Este é o "contrato" da Camada AI Provider. Qualquer modelo novo (Gemini,
DeepSeek, Mistral, Llama, Ollama, Grok, Cohere, Bedrock...) só precisa criar
uma classe que herde de `AIProvider` e implemente `generate()`. Nenhuma outra
parte do sistema precisa mudar — é o Princípio Aberto/Fechado (o "O" do SOLID)
em ação.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.ai.schemas import AIMessage, AIResponse


class AIProvider(ABC):
    """Classe base abstrata para todos os provedores de IA."""

    #: Nome curto do provedor (ex.: "claude", "openai"). Usado nos logs e
    #: na ordem de failover definida no `.env`.
    name: str = "base"

    @abstractmethod
    async def generate(
        self,
        messages: list[AIMessage],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> AIResponse:
        """Envia as mensagens ao modelo e retorna uma resposta padronizada.

        Args:
            messages: histórico da conversa já no formato padrão.
            system: instrução de sistema (personalidade/regras do agente).
            max_tokens: limite de tokens da resposta.

        Returns:
            AIResponse padronizado.

        Raises:
            AIProviderError: se a chamada ao modelo falhar.
        """
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """Indica se o provedor está pronto para uso (ex.: tem chave de API)."""
        raise NotImplementedError
