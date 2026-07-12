"""Provedor de IA: GPT (OpenAI) — modelo SECUNDÁRIO / de failover.

Serve como reserva: se o Claude ficar indisponível, o gerenciador alterna
automaticamente para este provedor, sem o cliente perceber a troca.
"""

from __future__ import annotations

from openai import AsyncOpenAI, OpenAIError

from app.ai.base import AIProvider
from app.ai.schemas import AIMessage, AIResponse, Role
from app.core.config import settings
from app.core.exceptions import AIProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIProvider(AIProvider):
    """Provedor que conversa com os modelos GPT da OpenAI."""

    name = "openai"

    def __init__(self) -> None:
        self._api_key = settings.openai_api_key
        self._model = settings.openai_model
        self._client = (
            AsyncOpenAI(api_key=self._api_key) if self._api_key else None
        )

    def is_available(self) -> bool:
        return self._client is not None

    async def generate(
        self,
        messages: list[AIMessage],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> AIResponse:
        if self._client is None:
            raise AIProviderError("OpenAI sem OPENAI_API_KEY configurada.")

        # Na OpenAI a instrução de sistema é uma mensagem com role="system"
        # no início da lista.
        api_messages: list[dict] = []
        if system:
            api_messages.append({"role": Role.SYSTEM.value, "content": system})
        api_messages.extend(
            {"role": m.role.value, "content": m.content} for m in messages
        )

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                max_tokens=max_tokens,
                messages=api_messages,
            )
        except OpenAIError as exc:
            logger.warning("Falha no provedor OpenAI: %s", exc)
            raise AIProviderError(f"OpenAI falhou: {exc}") from exc

        choice = response.choices[0]
        usage = response.usage

        return AIResponse(
            content=choice.message.content or "",
            provider=self.name,
            model=response.model,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
        )
