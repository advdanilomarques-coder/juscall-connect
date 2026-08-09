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

    async def complete(self, prefix: str, suffix: str, language: str, max_tokens: int = 96) -> str:
        """Fill-in-the-middle style code completion. Default = derive from chat.

        Kept deliberately terse so suggestions feel calm (Copilot-like)."""
        system = (
            "Você é um motor de autocomplete de código, como o GitHub Copilot. "
            "Regras: responda SOMENTE com o texto que vem imediatamente após o cursor; "
            "NÃO repita o que já foi escrito; NÃO explique; NÃO use blocos de código com crases; "
            "seja curto — normalmente 1 linha, no máximo poucas linhas, só o suficiente para "
            "completar a linha ou o bloco atual de forma natural."
        )
        prompt = (
            f"Linguagem: {language}\n"
            f"Complete a continuação no ponto <CURSOR>.\n\n"
            f"{prefix}<CURSOR>{suffix}"
        )
        result = await self.chat(
            [Message("system", system), Message("user", prompt)],
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
