# -*- coding: utf-8 -*-
"""Registro de ações relevantes para auditoria e conformidade com a LGPD."""
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_email: Mapped[Optional[str]] = mapped_column(String(180), nullable=True)
    acao: Mapped[str] = mapped_column(String(60), index=True)
    entidade: Mapped[str] = mapped_column(String(60), index=True)
    entidade_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    detalhes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    criado_em: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
