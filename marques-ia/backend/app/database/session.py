# -*- coding: utf-8 -*-
"""
Configuração da engine SQLAlchemy, da fábrica de sessões e da classe Base
usada por todos os modelos do projeto.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependência do FastAPI: abre uma sessão por requisição e garante o fechamento."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
