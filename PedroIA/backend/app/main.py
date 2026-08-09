"""PedroIA backend — FastAPI application entrypoint."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, chat, complete, crm, diag, health
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.core.ratelimit import RateLimitMiddleware
from app.database.session import init_db

settings = get_settings()
setup_logging("DEBUG" if settings.debug else "INFO")
logger = get_logger("pedroia")


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Iniciando PedroIA backend (%s)", settings.environment)
    # Safety net for hosted deployments: never run an open, billable backend in
    # production without at least one API key configured.
    # Warnings only — never crash the deploy over configuration.
    if settings.environment == "production" and not settings.auth_enabled:
        logger.warning("PRODUÇÃO sem API_KEYS: backend aberto. Defina API_KEYS para proteger e controlar custos.")
    if settings.jwt_secret == "change-me-in-production":
        logger.warning("JWT_SECRET não definido: usando segredo aleatório temporário (usuários deslogam a cada restart). Defina JWT_SECRET para sessões estáveis.")
    await init_db()
    yield
    logger.info("Encerrando PedroIA backend")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Backend do PedroIA — roteador multi-LLM (cloud + Ollama local), chat, autocomplete e CRM.",
    lifespan=lifespan,
)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    # Auth is via Authorization header (not cookies), so credentials aren't needed.
    # This keeps "*" origins valid for the public website.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(chat.router, prefix=settings.api_prefix)
app.include_router(complete.router, prefix=settings.api_prefix)
app.include_router(crm.router, prefix=settings.api_prefix)
app.include_router(diag.router, prefix=settings.api_prefix)


@app.get("/")
async def root() -> dict:
    return {"name": settings.app_name, "docs": "/docs", "health": f"{settings.api_prefix}/health"}
