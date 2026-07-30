"""Provedor de IA: DeepSeek — API compatível com OpenAI.

DeepSeek expõe uma API no padrão OpenAI, então só precisamos informar o
endpoint, a chave e o modelo. Endpoint oficial: https://api.deepseek.com
"""

from __future__ import annotations

from app.ai.providers.openai_compatible import OpenAICompatibleProvider
from app.core.config import settings


class DeepSeekProvider(OpenAICompatibleProvider):
    name = "deepseek"

    def __init__(self) -> None:
        super().__init__(
            base_url="https://api.deepseek.com/v1",
            api_key=settings.deepseek_api_key,
            model=settings.deepseek_model,
        )
