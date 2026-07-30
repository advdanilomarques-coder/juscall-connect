"""Dependências compartilhadas do FastAPI (Dependency Injection).

Centraliza as dependências reutilizadas pelas rotas:
  * `get_session`     → sessão de banco por requisição.
  * `get_current_admin`→ valida o JWT e retorna o admin autenticado.
  * `rate_limiter`     → instância única do limitador de requisições.

Usar dependências do FastAPI mantém as rotas limpas e testáveis (baixo
acoplamento) e centraliza regras transversais como autenticação.
"""

from __future__ import annotations

from typing import AsyncIterator

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AuthError
from app.core.rate_limit import InMemoryRateLimiter
from app.core.security import decode_access_token
from app.db.base import SessionLocal
from app.db.models import AdminUser

# Limitador de requisições único para toda a aplicação.
rate_limiter = InMemoryRateLimiter(settings.rate_limit_per_minute)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Fornece uma sessão de banco por requisição e a fecha ao final."""
    async with SessionLocal() as session:
        yield session


async def get_current_admin(
    authorization: str | None = Header(default=None),
    session: AsyncSession = Depends(get_session),
) -> AdminUser:
    """Valida o header `Authorization: Bearer <token>` e retorna o admin.

    Levanta 401 se o token faltar, for inválido/expirado, ou se o usuário
    não existir/estiver inativo. Protege todas as rotas administrativas.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso ausente.",
        )
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_access_token(token)
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc

    email = payload.get("sub")
    result = await session.execute(select(AdminUser).where(AdminUser.email == email))
    admin = result.scalar_one_or_none()
    if admin is None or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário administrador inválido ou inativo.",
        )
    return admin
