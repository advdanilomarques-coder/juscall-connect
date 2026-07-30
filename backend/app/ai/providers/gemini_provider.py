"""Provedor de IA: Google Gemini — modelo alternativo (camada GRATUITA).

Implementa a interface `AIProvider` usando o SDK oficial do Google
(google-generativeai). O Google AI Studio oferece uma chave de API gratuita,
sem cartão de crédito, ideal como reserva de baixo custo no failover.

Como obter a chave gratuita (leva menos de 2 minutos):
  1. Acesse https://aistudio.google.com/apikey
  2. Faça login com uma conta Google
  3. Clique em "Create API Key"
  4. Copie a chave e cole em GEMINI_API_KEY no arquivo .env

O SDK é importado de forma lazy (dentro dos métodos).
"""

from __future__ import annotations

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
        self._model_name = settings.gemini_model

    def is_available(self) -> bool:
        """Só está disponível se houver chave de API configurada."""
        return bool(self._api_key)

    async def generate(
        self,
        messages: list[AIMessage],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> AIResponse:
        if not self._api_key:
            raise AIProviderError("Gemini sem GEMINI_API_KEY configurada.")

        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise AIProviderError(
                "SDK 'google-generativeai' não instalado. "
                "Rode: pip install google-generativeai"
            ) from exc

        genai.configure(api_key=self._api_key)

        # O Gemini usa os papéis "user" e "model" (não "assistant" como
        # Claude/OpenAI). Convertendo o histórico padronizado do sistema:
        historico = [
            {
                "role": "model" if m.role == Role.ASSISTANT else "user",
                "parts": [m.content],
            }
            for m in messages
            if m.role != Role.SYSTEM
        ]

        modelo = genai.GenerativeModel(
            model_name=self._model_name,
            system_instruction=system,
        )

        try:
            response = await modelo.generate_content_async(
                historico,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                ),
            )
        except Exception as exc:
            # O SDK do Google não expõe uma única classe de exceção estável
            # entre versões; capturamos genericamente e encapsulamos no erro
            # de domínio (o AIManager sabe lidar com esse tipo).
            logger.warning("Falha no provedor Gemini: %s", exc)
            raise AIProviderError(f"Gemini falhou: {exc}") from exc

        usage = getattr(response, "usage_metadata", None)

        return AIResponse(
            content=response.text,
            provider=self.name,
            model=self._model_name,
            input_tokens=getattr(usage, "prompt_token_count", 0) if usage else 0,
            output_tokens=getattr(usage, "candidates_token_count", 0) if usage else 0,
        )
