# -*- coding: utf-8 -*-
"""
Marques IA — Backend + Agente de IA.

Ponto de entrada da aplicação FastAPI. Na inicialização:
  1. Cria as tabelas do banco (caso ainda não existam).
  2. Garante a existência do usuário administrador padrão (definido no .env).
  3. Sobe os routers de autenticação e do agente de IA.

Executar com:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
(a partir da pasta backend/, com o ambiente virtual ativado)
"""
import logging
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.api.routes_agent_health import router as agent_health_router
from app.api.routes_auth import router as auth_router
from app.api.routes_chat import router as chat_router
from app.api.routes_contracts import router as contracts_router
from app.api.routes_crm import router as crm_router
from app.api.routes_documents import router as documents_router
from app.api.routes_rag import router as rag_router
from app.api.routes_whatsapp import router as whatsapp_router
from app.core.config import settings
from app.core.security import hash_password
from app.database.session import Base, SessionLocal, engine
from app.models import (  # noqa: F401 — registra todas as tabelas
    AdminUser, BaseConhecimento, Caso, Cliente, Contrato, Documento, LogAuditoria, Mensagem,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("marques_ia")

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Backend e agente de IA do Marques IA — Marques Advogados Associados.",
)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(whatsapp_router)
app.include_router(crm_router)
app.include_router(contracts_router)
app.include_router(documents_router)
app.include_router(rag_router)
app.include_router(agent_health_router)

_static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/painel", StaticFiles(directory=_static_dir, html=True), name="painel")


def _criar_admin_padrao(db: Session) -> None:
    existente = db.query(AdminUser).filter(AdminUser.email == settings.ADMIN_DEFAULT_EMAIL).first()
    if existente:
        return

    admin = AdminUser(
        nome=settings.ADMIN_DEFAULT_NAME,
        email=settings.ADMIN_DEFAULT_EMAIL,
        senha_hash=hash_password(settings.ADMIN_DEFAULT_PASSWORD),
        papel="admin",
        ativo=True,
    )
    db.add(admin)
    db.commit()
    logger.info("Usuário administrador padrão criado: %s", settings.ADMIN_DEFAULT_EMAIL)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        _criar_admin_padrao(db)
    finally:
        db.close()

    logger.info(
        "Marques IA iniciado. WhatsApp: %s | Modelos de IA configurados: %s",
        settings.WHATSAPP_PHONE_NUMBER,
        settings.OPENROUTER_MODELS_ORDER,
    )


@app.get("/", tags=["status"])
def status_geral():
    """Endpoint de verificação rápida — confirma que a API e a configuração estão ok."""
    return {
        "app": settings.APP_NAME,
        "status": "online",
        "ambiente": settings.ENVIRONMENT,
        "whatsapp_numero": settings.WHATSAPP_PHONE_NUMBER,
        "modelos_ia_configurados": settings.OPENROUTER_MODELS_ORDER,
    }
