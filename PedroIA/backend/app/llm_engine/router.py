"""Model router: decides which provider serves a request.

    Internet disponível  ->  Modelo Cloud
    Sem internet         ->  Modelo Local (Ollama)
    Nada configurado     ->  Fallback (mensagem de configuração)

Mode overrides:
    auto  -> cloud if reachable, else local, else fallback
    cloud -> first available cloud provider (else local, else fallback)
    local -> Ollama only (else fallback)
"""
from __future__ import annotations

import socket
from typing import Dict, List, Optional

from app.core.config import get_settings
from app.core.logging import get_logger
from .providers import (
    AnthropicProvider,
    DeepSeekProvider,
    FallbackProvider,
    GeminiProvider,
    GroqProvider,
    LLMProvider,
    LLMResult,
    Message,
    OllamaProvider,
    OpenAIProvider,
    ProviderError,
)

logger = get_logger("pedroia.router")


def internet_available(host: str = "8.8.8.8", port: int = 53, timeout: float = 1.5) -> bool:
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except OSError:
        return False


class ModelRouter:
    def __init__(self) -> None:
        s = get_settings()
        self._cloud: Dict[str, LLMProvider] = {
            "anthropic": AnthropicProvider(),
            "openai": OpenAIProvider(),
            "groq": GroqProvider(),
            "gemini": GeminiProvider(),
            "deepseek": DeepSeekProvider(),
        }
        self._cloud_priority = s.cloud_priority
        self._ollama = OllamaProvider()
        self._fallback = FallbackProvider()

    # --- discovery ---
    def available_cloud(self) -> List[LLMProvider]:
        ordered = [self._cloud[n] for n in self._cloud_priority if n in self._cloud]
        return [p for p in ordered if p.is_available()]

    def status(self) -> dict:
        return {
            "online": internet_available(),
            "cloud_providers": [p.name for p in self.available_cloud()],
            "ollama": self._ollama.is_available(),
        }

    # --- selection ---
    def select(self, mode: str = "auto") -> LLMProvider:
        mode = (mode or "auto").lower()
        if mode == "local":
            return self._ollama if self._ollama.is_available() else self._fallback
        if mode == "cloud":
            cloud = self.available_cloud()
            if cloud:
                return cloud[0]
            return self._ollama if self._ollama.is_available() else self._fallback
        # auto
        if internet_available():
            cloud = self.available_cloud()
            if cloud:
                return cloud[0]
        if self._ollama.is_available():
            return self._ollama
        cloud = self.available_cloud()  # maybe connectivity check failed but keys work
        return cloud[0] if cloud else self._fallback

    # --- operations ---
    async def chat(self, messages: List[Message], mode: str = "auto", max_tokens: int = 1024) -> LLMResult:
        provider = self.select(mode)
        try:
            return await provider.chat(messages, max_tokens=max_tokens)
        except ProviderError as e:
            logger.warning("Provider %s failed (%s); trying fallback chain", provider.name, e)
            return await self._chat_with_fallbacks(messages, exclude=provider.name, max_tokens=max_tokens)

    async def _chat_with_fallbacks(self, messages: List[Message], exclude: str, max_tokens: int) -> LLMResult:
        candidates: List[LLMProvider] = [p for p in self.available_cloud() if p.name != exclude]
        if self._ollama.is_available() and exclude != "ollama":
            candidates.append(self._ollama)
        for p in candidates:
            try:
                return await p.chat(messages, max_tokens=max_tokens)
            except ProviderError as e:
                logger.warning("Fallback provider %s failed: %s", p.name, e)
        return await self._fallback.chat(messages, max_tokens=max_tokens)

    async def complete(self, prefix: str, suffix: str, language: str, mode: str = "auto", max_tokens: int = 128) -> LLMResult:
        # Prefer local for latency; fall back to selected provider.
        provider: Optional[LLMProvider] = None
        if mode in ("auto", "local") and self._ollama.is_available():
            provider = self._ollama
        if provider is None:
            provider = self.select(mode)
        try:
            text = await provider.complete(prefix, suffix, language, max_tokens=max_tokens)
            return LLMResult(content=text, model=getattr(provider, "completion_model", provider.name), provider=provider.name)
        except ProviderError as e:
            logger.warning("Completion via %s failed: %s", provider.name, e)
            return LLMResult(content="", model="none", provider="none")


_router: Optional[ModelRouter] = None


def get_router() -> ModelRouter:
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router
