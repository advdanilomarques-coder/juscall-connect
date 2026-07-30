# -*- coding: utf-8 -*-
"""Base de conhecimento jurídica — trechos de referência usados pelo RAG."""
from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class BaseConhecimento(Base):
    __tablename__ = "base_conhecimento"

    id: Mapped[int] = mapped_column(primary_key=True)
    area_juridica: Mapped[str] = mapped_column(String(40), index=True)
    titulo: Mapped[str] = mapped_column(String(200))
    conteudo: Mapped[str] = mapped_column(Text)
    criado_em: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
