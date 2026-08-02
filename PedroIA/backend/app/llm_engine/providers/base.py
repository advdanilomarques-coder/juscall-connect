"""Provider abstraction. Every LLM backend (cloud or local) implements this."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Message:
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMResult:
    content: str
    model: str
    provider: str


class LLMProvider(ABC):
    """Base class for chat + completion capable providers."""

    name: str = "base"

    @abstractmethod
    def is_available(self) -> bool:
        """Cheap, synchronous check for whether this provider is configured."""

    @abstractmethod
    async def chat(self, messages: List[Message], max_tokens: int = 1024) -> LLMResult:
        ...

    async def complete(self, prefix: str, suffix: str, language: str, max_tokens: int = 128) -> str:
        """Fill-in-the-middle style code completion. Default = derive from chat."""
        prompt = (
            f"Complete o código {language} a seguir. Responda APENAS com o código que vem "
            f"logo após o cursor, sem explicações e sem repetir o que já existe.\n\n"
            f"<antes>\n{prefix}\n</antes>\n<depois>\n{suffix}\n</depois>"
        )
        result = await self.chat(
            [
                Message("system", "Você é um motor de autocomplete de código. Responda só com código."),
                Message("user", prompt),
            ],
            max_tokens=max_tokens,
        )
        return _strip_code_fence(result.content)


def _strip_code_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines)
    return text


class ProviderError(RuntimeError):
    pass
