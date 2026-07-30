# -*- coding: utf-8 -*-
"""Modelo de usuário do painel administrativo (autenticação JWT)."""
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class AdminUser(Base):
    __tablename__ = "usuarios_admin"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    papel: Mapped[str] = mapped_column(String(30), default="admin")
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
