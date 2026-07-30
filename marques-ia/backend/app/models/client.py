# -*- coding: utf-8 -*-
"""Modelo de cliente — identificado pelo telefone (mesmo número do WhatsApp)."""
from typing import Optional

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True)
    telefone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    nome: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(180), nullable=True)
    criado_em: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ultimo_contato_em: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
