"""Async SQLAlchemy engine/session setup.

Normalizes common Postgres URLs (Render/Neon/Supabase/Heroku) so they work with
the async `asyncpg` driver:
  - postgres://          -> postgresql+asyncpg://
  - postgresql://        -> postgresql+asyncpg://
  - ?sslmode=require etc -> stripped, TLS passed via connect_args (asyncpg style)
"""
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()


def _normalize_db_url(url: str) -> tuple[str, dict]:
    connect_args: dict = {}
    if url.startswith("postgres://"):
        url = "postgresql+asyncpg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+asyncpg://" + url[len("postgresql://"):]

    if url.startswith("postgresql+asyncpg://"):
        parts = urlsplit(url)
        query = dict(parse_qsl(parts.query))
        # asyncpg doesn't accept libpq's sslmode/channel_binding in the URL.
        sslmode = query.pop("sslmode", None)
        query.pop("channel_binding", None)
        if sslmode and sslmode != "disable":
            connect_args["ssl"] = True
        url = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))
    return url, connect_args


_db_url, _connect_args = _normalize_db_url(settings.database_url)

engine = create_async_engine(
    _db_url,
    echo=False,
    future=True,
    pool_pre_ping=True,  # survive dropped connections on free-tier Postgres
    connect_args=_connect_args,
)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    from app.database import models  # noqa: F401  (register tables)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:  # FastAPI dependency
    async with AsyncSessionLocal() as session:
        yield session
