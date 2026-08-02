"""PedroIA backend — FastAPI application entrypoint."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, complete, crm, health
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.database.session import init_db

settings = get_settings()
setup_logging("DEBUG" if settings.debug else "INFO")
logger = get_logger("pedroia")


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Iniciando PedroIA backend (%s)", settings.environment)
    await init_db()
    yield
    logger.info("Encerrando PedroIA backend")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Backend do PedroIA — roteador multi-LLM (cloud + Ollama local), chat, autocomplete e CRM.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(chat.router, prefix=settings.api_prefix)
app.include_router(complete.router, prefix=settings.api_prefix)
app.include_router(crm.router, prefix=settings.api_prefix)


@app.get("/")
async def root() -> dict:
    return {"name": settings.app_name, "docs": "/docs", "health": f"{settings.api_prefix}/health"}
