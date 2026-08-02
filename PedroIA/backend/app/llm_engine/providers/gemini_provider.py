"""Google Gemini chat provider via the Generative Language API."""
from typing import List

import httpx

from app.core.config import get_settings
from .base import LLMProvider, LLMResult, Message, ProviderError


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self):
        s = get_settings()
        self.api_key = s.gemini_api_key
        self.model = s.gemini_model

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def chat(self, messages: List[Message], max_tokens: int = 1024) -> LLMResult:
        system = "\n\n".join(m.content for m in messages if m.role == "system")
        contents = []
        for m in messages:
            if m.role == "system":
                continue
            role = "model" if m.role == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": m.content}]})
        payload = {
            "contents": contents,
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.2},
        }
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(url, json=payload)
        if resp.status_code >= 400:
            raise ProviderError(f"gemini {resp.status_code}: {resp.text[:200]}")
        data = resp.json()
        try:
            content = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            content = ""
        return LLMResult(content=content, model=self.model, provider=self.name)
