"""Provedor de IA: Grok (xAI) — API compatível com OpenAI.

Endpoint oficial: https://api.x.ai/v1
"""

from __future__ import annotations

from app.ai.providers.openai_compatible import OpenAICompatibleProvider
from app.core.config import settings


class GrokProvider(OpenAICompatibleProvider):
    name = "grok"

    def __init__(self) -> None:
        super().__init__(
            base_url="https://api.x.ai/v1",
            api_key=settings.grok_api_key,
            model=settings.grok_model,
        )
