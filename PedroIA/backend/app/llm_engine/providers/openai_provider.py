"""OpenAI (and OpenAI-compatible, e.g. DeepSeek) chat provider via HTTP."""
from typing import List

import httpx

from app.core.config import get_settings
from .base import LLMProvider, LLMResult, Message, ProviderError


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, api_key: str = "", model: str = "", base_url: str = "https://api.openai.com/v1", name: str = "openai"):
        s = get_settings()
        self.name = name
        self.api_key = api_key or s.openai_api_key
        self.model = model or s.openai_model
        self.base_url = base_url.rstrip("/")

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def chat(self, messages: List[Message], max_tokens: int = 1024) -> LLMResult:
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "max_tokens": max_tokens,
            "temperature": 0.2,
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
        if resp.status_code >= 400:
            raise ProviderError(f"{self.name} {resp.status_code}: {resp.text[:200]}")
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return LLMResult(content=content, model=self.model, provider=self.name)


class DeepSeekProvider(OpenAIProvider):
    """DeepSeek is OpenAI-API compatible."""

    def __init__(self):
        s = get_settings()
        super().__init__(
            api_key=s.deepseek_api_key,
            model=s.deepseek_model,
            base_url="https://api.deepseek.com/v1",
            name="deepseek",
        )


class GroqProvider(OpenAIProvider):
    """Groq is OpenAI-API compatible; generous free tier, no billing required."""

    def __init__(self):
        s = get_settings()
        super().__init__(
            api_key=s.groq_api_key,
            model=s.groq_model,
            base_url="https://api.groq.com/openai/v1",
            name="groq",
        )
