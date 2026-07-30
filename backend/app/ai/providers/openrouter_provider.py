"""Provedor de IA: OpenRouter — roteador para dezenas de modelos.

O OpenRouter dá acesso a modelos de vários fornecedores por uma única API
compatível com OpenAI. O modelo é escolhido no campo `model` (ex.:
"anthropic/claude-3.5-sonnet", "meta-llama/llama-3.1-70b-instruct").

Endpoint oficial: https://openrouter.ai/api/v1
"""

from __future__ import annotations

from app.ai.providers.openai_compatible import OpenAICompatibleProvider
from app.core.config import settings


class OpenRouterProvider(OpenAICompatibleProvider):
    name = "openrouter"

    def __init__(self) -> None:
        super().__init__(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
            model=settings.openrouter_model,
            # Cabeçalhos recomendados pelo OpenRouter para identificar o app.
            extra_headers={
                "HTTP-Referer": "https://marquesadvogados.com.br",
                "X-Title": settings.app_name,
            },
        )
