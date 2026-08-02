"""Test fixtures. Uses a throwaway SQLite DB and creates tables up front,
since httpx's ASGITransport does not trigger the app's lifespan/startup."""
import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_pedroia.db")

import pytest_asyncio  # noqa: E402

from app.database.session import Base, engine  # noqa: E402


@pytest_asyncio.fixture(autouse=True)
async def _create_schema():
    from app.database import models  # noqa: F401  (register tables)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
