# -*- coding: utf-8 -*-
"""Documentos anexados a um caso (imagens ou PDFs digitalizados), com texto via OCR."""
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class Documento(Base):
    __tablename__ = "documentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    caso_id: Mapped[int] = mapped_column(ForeignKey("casos.id"), index=True)

    nome_arquivo: Mapped[str] = mapped_column(String(255))
    tipo: Mapped[str] = mapped_column(String(20))  # "pdf" ou "image"
    caminho_arquivo: Mapped[str] = mapped_column(String(255))

    texto_ocr: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confianca_ocr: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    upload_em: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
