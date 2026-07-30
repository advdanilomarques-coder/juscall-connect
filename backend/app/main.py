"""Ponto de entrada da aplicação (FastAPI) — integra todas as camadas.

Rotas registradas:
  * GET  /                         → healthcheck / status da aplicação.
  * /chat/*                        → atendimento genérico (site/widget).
  * /channels/whatsapp/webhook     → integração WhatsApp Business API.
  * /admin/*                       → painel administrativo (JWT).
  * /crm/*                         → CRM: leads, funil/kanban, tarefas, notas.
  * /documents/*                   → upload/organização de documentos.
  * /contracts/*                   → geração automática de contratos em PDF.

No startup (lifespan): cria as tabelas do banco e semeia o admin inicial.

Executar em desenvolvimento:
    uvicorn app.main:app --reload
Documentação interativa: http://localhost:8000/docs
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.admin.router import router as admin_router
from app.admin.service import seed_admin
from app.channels.router import router as channels_router
from app.channels.whatsapp import whatsapp_client
from app.chat.router import router as chat_router
from app.contracts.router import router as contracts_router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.crm.router import router as crm_router
from app.db.base import init_db
from app.documents.router import router as documents_router

# Configura os logs assim que o módulo é carregado.
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida: cria tabelas e semeia o admin inicial no startup."""
    await init_db()
    await seed_admin()
    logger.info(
        "Aplicação iniciada: %s (env=%s) | provedores de IA: %s",
        settings.app_name,
        settings.app_env,
        ", ".join(settings.provider_order) or "nenhum",
    )
    yield


app = FastAPI(
    title=settings.app_name,
    description="Agente de IA Jurídico — Marques Advogados Associados.",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan,
)

# CORS: libera o front-end do CRM a consumir a API. Em produção, restrinja
# `allow_origins` aos domínios reais do painel.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro dos módulos (cada um com sua responsabilidade única).
app.include_router(chat_router)
app.include_router(channels_router)
app.include_router(admin_router)
app.include_router(crm_router)
app.include_router(documents_router)
app.include_router(contracts_router)


@app.get("/", tags=["Sistema"])
async def health() -> dict:
    """Healthcheck — confirma que a aplicação está no ar e mostra o status."""
    return {
        "app": settings.app_name,
        "env": settings.app_env,
        "status": "ok",
        "firm": settings.firm_name,
        "whatsapp_configured": whatsapp_client.configured,
    }
