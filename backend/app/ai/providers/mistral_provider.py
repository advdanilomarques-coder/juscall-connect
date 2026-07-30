"""Provedor de IA: Mistral AI — API compatível com OpenAI.

Endpoint oficial: https://api.mistral.ai/v1
"""

from __future__ import annotations

from app.ai.providers.openai_compatible import OpenAICompatibleProvider
from app.core.config import settings


class MistralProvider(OpenAICompatibleProvider):
    name = "mistral"

    def __init__(self) -> None:
        super().__init__(
            base_url="https://api.mistral.ai/v1",
            api_key=settings.mistral_api_key,
            model=settings.mistral_model,
        )
