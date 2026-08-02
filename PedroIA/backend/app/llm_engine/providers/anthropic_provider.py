"""Anthropic (Claude) chat provider via the Messages API."""
from typing import List

import httpx

from app.core.config import get_settings
from .base import LLMProvider, LLMResult, Message, ProviderError


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self):
        s = get_settings()
        self.api_key = s.anthropic_api_key
        self.model = s.anthropic_model

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def chat(self, messages: List[Message], max_tokens: int = 1024) -> LLMResult:
        system = "\n\n".join(m.content for m in messages if m.role == "system")
        convo = [{"role": m.role, "content": m.content} for m in messages if m.role in ("user", "assistant")]
        payload = {"model": self.model, "max_tokens": max_tokens, "messages": convo}
        if system:
            payload["system"] = system
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers)
        if resp.status_code >= 400:
            raise ProviderError(f"anthropic {resp.status_code}: {resp.text[:200]}")
        data = resp.json()
        parts = [b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"]
        return LLMResult(content="".join(parts), model=self.model, provider=self.name)
