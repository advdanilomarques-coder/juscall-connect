# -*- coding: utf-8 -*-
"""Modelo de Contrato — documento em PDF gerado a partir de um caso."""
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class Contrato(Base):
    __tablename__ = "contratos"

    id: Mapped[int] = mapped_column(primary_key=True)
    caso_id: Mapped[int] = mapped_column(ForeignKey("casos.id"), index=True)

    tipo: Mapped[str] = mapped_column(String(60))
    arquivo_pdf_path: Mapped[str] = mapped_column(String(255))
    # rascunho -> aguarda revisão humana | aprovado -> liberado para envio | enviado
    status: Mapped[str] = mapped_column(String(20), default="rascunho")
    numero: Mapped[Optional[str]] = mapped_column(String(40), nullable=True, unique=True)

    gerado_em: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
