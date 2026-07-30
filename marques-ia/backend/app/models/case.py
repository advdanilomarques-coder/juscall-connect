# -*- coding: utf-8 -*-
"""Modelo de Caso — cada processo/atendimento aberto, vinculado a um cliente."""
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base

# Etapas padrão do funil kanban (ordem sugerida de progresso).
ETAPAS_FUNIL = [
    "novo_lead",
    "qualificacao",
    "documentacao",
    "proposta",
    "contrato",
    "fechado",
]

AREAS_JURIDICAS = [
    "direito_bancario",
    "acao_revisional",
    "busca_e_apreensao",
    "cnh_area_medica",
    "outro",
]


class Caso(Base):
    __tablename__ = "casos"

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), index=True)

    area_juridica: Mapped[str] = mapped_column(String(40), default="outro")
    etapa_funil: Mapped[str] = mapped_column(String(30), default="novo_lead", index=True)
    status: Mapped[str] = mapped_column(String(20), default="aberto")  # aberto | encerrado
    responsavel: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    resumo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    criado_em: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
