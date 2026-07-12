"""Modelos ORM — as tabelas que guardam a memória do agente.

Modelagem baseada nas seções MEMÓRIA e ETAPAS DO CRM do documento do projeto:
  * Lead          → o cliente/potencial cliente e seus dados cadastrais.
  * Conversation  → um atendimento (thread de conversa) de um lead.
  * Message       → cada mensagem trocada (do cliente ou do agente).

A memória é INDEPENDENTE do modelo de IA: guardamos qual provedor/modelo
respondeu apenas como metadado, mas o histórico em si é neutro.
"""

from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _now() -> datetime:
    """Data/hora atual em UTC (timezone-aware)."""
    return datetime.now(timezone.utc)


class LeadStatus(str, enum.Enum):
    """Etapas do funil do CRM (conforme 'ETAPAS DO CRM' no documento)."""

    NOVO_LEAD = "novo_lead"
    PRIMEIRO_ATENDIMENTO = "primeiro_atendimento"
    ANALISE_JURIDICA = "analise_juridica"
    DOCUMENTACAO_PENDENTE = "documentacao_pendente"
    DOCUMENTACAO_RECEBIDA = "documentacao_recebida"
    CONTRATO_GERADO = "contrato_gerado"
    CONTRATO_ENVIADO = "contrato_enviado"
    CONTRATO_ASSINADO = "contrato_assinado"
    PAGAMENTO = "pagamento"
    PROCESSO_EM_ANDAMENTO = "processo_em_andamento"
    CLIENTE_FINALIZADO = "cliente_finalizado"
    ARQUIVADO = "arquivado"


class Lead(Base):
    """Cliente/lead e seus dados cadastrais (memória de longo prazo)."""

    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Identificação (o telefone do WhatsApp é a chave natural).
    phone: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    state: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Contexto do atendimento.
    problem: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[LeadStatus] = mapped_column(
        SAEnum(LeadStatus), default=LeadStatus.NOVO_LEAD, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_now, onupdate=_now
    )

    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="lead", cascade="all, delete-orphan"
    )


class Conversation(Base):
    """Um atendimento (thread) pertencente a um lead."""

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lead_id: Mapped[int] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    lead: Mapped[Lead] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(Base):
    """Uma mensagem individual da conversa (do cliente ou do agente)."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), index=True
    )

    # "user" (cliente) ou "assistant" (agente).
    role: Mapped[str] = mapped_column(String(32))
    content: Mapped[str] = mapped_column(Text)

    # Metadados de IA (controle de custos e auditoria). Neutros em relação
    # ao conteúdo — a memória continua independente do modelo.
    provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    conversation: Mapped[Conversation] = relationship(back_populates="messages")
