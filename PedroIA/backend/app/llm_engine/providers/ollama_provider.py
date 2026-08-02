"""Ollama local provider — powers offline mode (Llama / Mistral / Qwen, etc.)."""
from typing import List

import httpx

from app.core.config import get_settings
from .base import LLMProvider, LLMResult, Message, ProviderError, _strip_code_fence


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self):
        s = get_settings()
        self.base_url = s.ollama_base_url.rstrip("/")
        self.model = s.ollama_model
        self.completion_model = s.ollama_completion_model

    def is_available(self) -> bool:
        """Available if the local Ollama daemon answers."""
        try:
            resp = httpx.get(f"{self.base_url}/api/tags", timeout=1.5)
            return resp.status_code == 200
        except Exception:
            return False

    async def chat(self, messages: List[Message], max_tokens: int = 1024) -> LLMResult:
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "options": {"num_predict": max_tokens, "temperature": 0.2},
        }
        async with httpx.AsyncClient(timeout=300) as client:
            resp = await client.post(f"{self.base_url}/api/chat", json=payload)
        if resp.status_code >= 400:
            raise ProviderError(f"ollama {resp.status_code}: {resp.text[:200]}")
        data = resp.json()
        content = data.get("message", {}).get("content", "")
        return LLMResult(content=content, model=self.model, provider=self.name)

    async def complete(self, prefix: str, suffix: str, language: str, max_tokens: int = 128) -> str:
        # Use Ollama's native fill-in-the-middle via the /api/generate suffix param.
        payload = {
            "model": self.completion_model,
            "prompt": prefix,
            "suffix": suffix,
            "stream": False,
            "options": {"num_predict": max_tokens, "temperature": 0.1, "stop": ["\n\n\n"]},
        }
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(f"{self.base_url}/api/generate", json=payload)
        if resp.status_code >= 400:
            raise ProviderError(f"ollama {resp.status_code}: {resp.text[:200]}")
        return _strip_code_fence(resp.json().get("response", ""))
