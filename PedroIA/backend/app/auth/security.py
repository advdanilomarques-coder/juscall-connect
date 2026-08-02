"""Optional API-key auth. Disabled automatically when no keys are configured (local mode)."""
from fastapi import Header, HTTPException, status

from app.core.config import get_settings


async def require_api_key(authorization: str = Header(default="")) -> None:
    settings = get_settings()
    if not settings.auth_enabled:
        return  # local mode: open
    token = authorization.removeprefix("Bearer ").strip()
    if token not in settings.allowed_api_keys:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Chave de API inválida.")
