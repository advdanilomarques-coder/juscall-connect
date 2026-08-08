"""Access control.

- require_api_key: admin endpoints (CRM, diag). API key only.
- require_access:  chat/completion. Accepts an API key OR a valid user JWT
  (so both the VS Code extension and logged-in website users can use it).
- Auth is disabled entirely when no API keys are configured (local dev).
"""
from fastapi import Header, HTTPException, status

from app.auth.passwords import decode_token
from app.core.config import get_settings


def _bearer(authorization: str) -> str:
    return authorization.removeprefix("Bearer ").removeprefix("bearer ").strip()


async def require_api_key(authorization: str = Header(default="")) -> None:
    settings = get_settings()
    if not settings.auth_enabled:
        return
    if _bearer(authorization) not in settings.allowed_api_keys:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Chave de API inválida.")


async def require_access(authorization: str = Header(default="")) -> str:
    """Returns the caller identity ('apikey' or the user email)."""
    settings = get_settings()
    token = _bearer(authorization)

    # Accept a configured API key (used by the VS Code extension).
    if settings.auth_enabled and token in settings.allowed_api_keys:
        return "apikey"

    # Accept a valid user JWT (used by the website).
    payload = decode_token(token) if token else None
    if payload and payload.get("sub"):
        return str(payload["sub"])

    # Local mode with no auth configured: open.
    if not settings.auth_enabled:
        return "anonymous"

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autorizado. Faça login ou informe uma chave válida.")
