"""Infraestrutura do banco de dados (SQLAlchemy async).

Cria o `engine` (conexão), a fábrica de sessões e a função de inicialização
que cria as tabelas. O mesmo código atende SQLite e PostgreSQL — basta mudar
a `DATABASE_URL` no `.env`.
"""

from __future__ import annotations

import os

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """Classe base de todos os modelos ORM (tabelas)."""


# Engine assíncrono compartilhado por toda a aplicação.
engine = create_async_engine(settings.database_url, echo=False, future=True)

# Fábrica de sessões. `expire_on_commit=False` permite usar objetos após o
# commit sem consultas extras ao banco.
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


def _ensure_sqlite_dir() -> None:
    """Garante que a pasta do arquivo SQLite exista (ex.: ./storage)."""
    url = settings.database_url
    if "sqlite" in url and ":///" in url:
        path = url.split(":///", 1)[1].split("?", 1)[0]
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)


async def init_db() -> None:
    """Cria as tabelas no banco (idempotente — seguro rodar sempre)."""
    _ensure_sqlite_dir()
    # Importa os modelos para que sejam registrados no metadata antes do
    # create_all. O import fica aqui dentro para evitar import circular.
    from app.db import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Banco de dados inicializado (%s).", settings.database_url)
