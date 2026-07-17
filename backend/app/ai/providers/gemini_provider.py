"""Provedor de IA: Gemini (Google) — opção GRATUITA.

Implementa a interface `AIProvider` usando o SDK oficial do Google (google-genai).
O Gemini possui uma cota gratuita generosa, ideal para desenvolvimento e testes
sem custo. Graças à camada de abstração, ele se encaixa no sistema exatamente
como o Claude e o GPT — sem alterar CRM, memória ou atendimento.
"""

from __future__ import annotations

from google import genai
from google.genai import types

from app.ai.base import AIProvider
from app.ai.schemas import AIMessage, AIResponse, Role
from app.core.config import settings
from app.core.exceptions import AIProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)


class GeminiProvider(AIProvider):
    """Provedor que conversa com os modelos Gemini do Google."""

    name = "gemini"

    def __init__(self) -> None:
        self._api_key = settings.gemini_api_key
        self._model = settings.gemini_model
        # Só cria o cliente se houver chave; caso contrário fica indisponível.
        self._client = (
            genai.Client(api_key=self._api_key) if self._api_key else None
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
            raise AIProviderError("Gemini sem GEMINI_API_KEY configurada.")

        # Converte o histórico padronizado para o formato do Gemini.
        # No Gemini os papéis são "user" e "model" (não "assistant").
        contents: list[types.Content] = []
        for m in messages:
            if m.role == Role.SYSTEM:
                continue  # a instrução de sistema vai no config, separada
            role = "user" if m.role == Role.USER else "model"
            contents.append(
                types.Content(role=role, parts=[types.Part(text=m.content)])
            )

        config = types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            system_instruction=system or None,
        )

        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=contents,
                config=config,
            )
        except Exception as exc:  # noqa: BLE001 (qualquer falha aciona o failover)
            logger.warning("Falha no provedor Gemini: %s", exc)
            raise AIProviderError(f"Gemini falhou: {exc}") from exc

        # Metadados de uso (podem não vir em todos os casos).
        usage = response.usage_metadata
        input_tokens = getattr(usage, "prompt_token_count", 0) or 0
        output_tokens = getattr(usage, "candidates_token_count", 0) or 0

        return AIResponse(
            content=response.text or "",
            provider=self.name,
            model=self._model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
