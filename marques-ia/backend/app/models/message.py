# -*- coding: utf-8 -*-
"""Histórico de mensagens trocadas com cada cliente (memória do agente)."""
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class Mensagem(Base):
    __tablename__ = "mensagens"

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), index=True)
    role: Mapped[str] = mapped_column(String(20))  # "user" ou "assistant"
    conteudo: Mapped[str] = mapped_column(Text)
    criado_em: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
