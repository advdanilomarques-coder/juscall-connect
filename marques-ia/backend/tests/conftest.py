# -*- coding: utf-8 -*-
"""
Configuração compartilhada dos testes. Define variáveis de ambiente mínimas
ANTES de qualquer import do pacote app (necessário porque app.core.config.Settings
exige DATABASE_URL, SECRET_KEY e OPENROUTER_API_KEY sem valor padrão).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("OPENROUTER_API_KEY", "test-openrouter-key")
os.environ.setdefault("WHATSAPP_APP_SECRET", "test-app-secret")

import pytest  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.database.session import Base  # noqa: E402
from app.models import AdminUser, Caso, Cliente, Contrato, LogAuditoria, Mensagem  # noqa: E402,F401


@pytest.fixture()
def db_session():
    """Sessão de banco SQLite em memória, isolada por teste."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
