"""Last-resort provider so PedroIA always responds, even with no keys and no Ollama.

It is intentionally not an LLM — it returns a helpful, deterministic message telling
the user how to enable a real model. This keeps the whole stack runnable out of the box.
"""
from typing import List

from .base import LLMProvider, LLMResult, Message


class FallbackProvider(LLMProvider):
    name = "fallback"

    def is_available(self) -> bool:
        return True

    async def chat(self, messages: List[Message], max_tokens: int = 1024) -> LLMResult:
        msg = (
            "⚙️ **Clean Code está sem um modelo de IA ativo.**\n\n"
            "O servidor está no ar, mas nenhuma chave de modelo foi encontrada. "
            "Defina **uma** destas variáveis no servidor (Render → Environment) e faça o deploy:\n\n"
            "`GROQ_API_KEY` (grátis, recomendado) · `ANTHROPIC_API_KEY` · `OPENAI_API_KEY` · `GEMINI_API_KEY`\n\n"
            "Depois teste em `/api/v1/diag` para confirmar que o provedor respondeu."
        )
        return LLMResult(content=msg, model="none", provider=self.name)

    async def complete(self, prefix: str, suffix: str, language: str, max_tokens: int = 128) -> str:
        return ""
