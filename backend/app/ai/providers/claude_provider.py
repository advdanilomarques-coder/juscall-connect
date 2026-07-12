"""Provedor de IA: Claude (Anthropic) — modelo PRINCIPAL do sistema.

Implementa a interface `AIProvider` usando o SDK oficial da Anthropic.
Modelo padrão: `claude-opus-4-8`.
"""

from __future__ import annotations

import anthropic

from app.ai.base import AIProvider
from app.ai.schemas import AIMessage, AIResponse, Role
from app.core.config import settings
from app.core.exceptions import AIProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)


class ClaudeProvider(AIProvider):
    """Provedor que conversa com os modelos Claude da Anthropic."""

    name = "claude"

    def __init__(self) -> None:
        # Cliente assíncrono; se não houver chave, ele fica None e o provedor
        # se reporta como indisponível (usado no failover).
        self._api_key = settings.anthropic_api_key
        self._model = settings.claude_model
        self._client = (
            anthropic.AsyncAnthropic(api_key=self._api_key) if self._api_key else None
        )

    def is_available(self) -> bool:
        """Só está disponível se houver chave de API configurada."""
        return self._client is not None

    async def generate(
        self,
        messages: list[AIMessage],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> AIResponse:
        if self._client is None:
            raise AIProviderError("Claude sem ANTHROPIC_API_KEY configurada.")

        # Converte o histórico padronizado para o formato do SDK da Anthropic.
        # A mensagem de sistema NÃO entra na lista `messages` — vai no campo
        # `system` separado (regra da API da Anthropic).
        api_messages = [
            {"role": m.role.value, "content": m.content}
            for m in messages
            if m.role != Role.SYSTEM
        ]

        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                system=system or anthropic.NOT_GIVEN,
                messages=api_messages,
            )
        except anthropic.APIError as exc:
            # Encapsula o erro do SDK na nossa exceção de domínio para que o
            # gerenciador consiga acionar o failover.
            logger.warning("Falha no provedor Claude: %s", exc)
            raise AIProviderError(f"Claude falhou: {exc}") from exc

        # A resposta pode conter vários blocos; juntamos apenas os de texto.
        text = "".join(block.text for block in response.content if block.type == "text")

        return AIResponse(
            content=text,
            provider=self.name,
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )
