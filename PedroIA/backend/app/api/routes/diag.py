"""Diagnostic endpoint: tries a real call on each configured provider and
reports the raw error. Makes it easy to see WHY a provider falls back
(wrong model, invalid key, API not enabled, region, quota, etc.)."""
from fastapi import APIRouter, Depends

from app.auth.security import require_api_key
from app.core.config import get_settings
from app.llm_engine.providers import Message
from app.llm_engine.router import get_router, internet_available

router = APIRouter(tags=["diag"], dependencies=[Depends(require_api_key)])


@router.get("/diag")
async def diag() -> dict:
    settings = get_settings()
    r = get_router()
    results: dict = {
        "online": internet_available(),
        "resolved_models": {
            "gemini": settings.gemini_model,
            "openai": settings.openai_model,
            "anthropic": settings.anthropic_model,
            "deepseek": settings.deepseek_model,
            "ollama": settings.ollama_model,
        },
        "providers": {},
    }

    # Only test cloud providers that have a key configured.
    for provider in r.available_cloud():
        entry: dict = {"available": True}
        try:
            out = await provider.chat([Message("user", "ping")], max_tokens=8)
            entry["ok"] = True
            entry["sample"] = (out.content or "")[:80]
            entry["model"] = out.model
        except Exception as e:  # noqa: BLE001
            entry["ok"] = False
            entry["error"] = str(e)[:400]
        results["providers"][provider.name] = entry

    if not results["providers"]:
        results["note"] = "Nenhum provedor de nuvem com chave configurada foi encontrado."
    return results
