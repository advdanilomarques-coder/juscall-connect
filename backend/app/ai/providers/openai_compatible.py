"""Provedor base para APIs compatíveis com o padrão OpenAI (`/chat/completions`).

Muitos provedores modernos (DeepSeek, Mistral, OpenRouter, Grok/xAI, Ollama e
outros) expõem uma API HTTP idêntica à da OpenAI. Em vez de repetir código,
centralizamos aqui a lógica comum usando `httpx` (cliente HTTP assíncrono).

Cada provedor concreto herda desta classe e informa apenas:
  * `name`      → nome curto (usado no failover/logs).
  * base_url    → endpoint da API.
  * api_key     → chave (pode ser vazia no caso do Ollama local).
  * model       → modelo padrão.

Isto é o Princípio Aberto/Fechado + DRY em ação: adicionar um provedor
compatível vira uma classe de poucas linhas.
"""

from __future__ import annotations

from app.ai.base import AIProvider
from app.ai.schemas import AIMessage, AIResponse, Role
from app.core.exceptions import AIProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenAICompatibleProvider(AIProvider):
    """Base para qualquer API compatível com o formato OpenAI Chat Completions."""

    name = "openai_compatible"

    #: Alguns provedores (Ollama local) não exigem chave de API.
    requires_key: bool = True

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._extra_headers = extra_headers or {}

    def is_available(self) -> bool:
        """Disponível se tiver chave (ou se o provedor dispensar chave)."""
        return bool(self._api_key) or not self.requires_key

    async def generate(
        self,
        messages: list[AIMessage],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> AIResponse:
        if self.requires_key and not self._api_key:
            raise AIProviderError(f"{self.name}: chave de API não configurada.")

        try:
            import httpx
        except ImportError as exc:
            raise AIProviderError(
                "Biblioteca 'httpx' não instalada. Rode: pip install httpx"
            ) from exc

        # Monta as mensagens no formato OpenAI (system como primeira mensagem).
        api_messages: list[dict] = []
        if system:
            api_messages.append({"role": Role.SYSTEM.value, "content": system})
        api_messages.extend(
            {"role": m.role.value, "content": m.content} for m in messages
        )

        headers = {"Content-Type": "application/json", **self._extra_headers}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        payload = {
            "model": self._model,
            "messages": api_messages,
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            logger.warning("Falha no provedor %s: %s", self.name, exc)
            raise AIProviderError(f"{self.name} falhou: {exc}") from exc

        try:
            content = data["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as exc:
            raise AIProviderError(
                f"{self.name}: resposta em formato inesperado: {data}"
            ) from exc

        usage = data.get("usage") or {}
        return AIResponse(
            content=content,
            provider=self.name,
            model=data.get("model", self._model),
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
        )
