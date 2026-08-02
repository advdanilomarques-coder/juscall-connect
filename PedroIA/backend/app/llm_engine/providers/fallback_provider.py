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
        last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        msg = (
            "⚙️ **PedroIA está em modo de configuração.**\n\n"
            "Nenhum modelo de IA está ativo ainda. Para habilitar respostas reais, escolha uma opção:\n\n"
            "**Nuvem** — defina uma chave no `backend/.env`:\n"
            "```\nANTHROPIC_API_KEY=...\n# ou OPENAI_API_KEY / GEMINI_API_KEY / DEEPSEEK_API_KEY\n```\n\n"
            "**Local (offline)** — instale o Ollama e baixe um modelo:\n"
            "```\nollama pull llama3.1\n```\n\n"
            f"Sua mensagem foi recebida: _{last_user[:200]}_"
        )
        return LLMResult(content=msg, model="none", provider=self.name)

    async def complete(self, prefix: str, suffix: str, language: str, max_tokens: int = 128) -> str:
        return ""
