"""Provedor de IA: Ollama — modelos LOCAIS (sem custo, sem chave).

Ollama roda modelos abertos (Llama, Mistral, Qwen, etc.) na própria máquina
ou servidor. Expõe uma API compatível com OpenAI em `/v1`. Como é local, não
exige chave de API — por isso `requires_key = False`.

Servidor padrão: http://localhost:11434 (configurável via OLLAMA_BASE_URL).
"""

from __future__ import annotations

from app.ai.providers.openai_compatible import OpenAICompatibleProvider
from app.core.config import settings


class OllamaProvider(OpenAICompatibleProvider):
    name = "ollama"
    requires_key = False  # Ollama local não usa chave de API.

    def __init__(self) -> None:
        super().__init__(
            base_url=f"{settings.ollama_base_url.rstrip('/')}/v1",
            api_key="",
            model=settings.ollama_model,
        )
