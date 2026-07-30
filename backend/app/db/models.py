"""Modelos ORM — as tabelas do sistema (memória do agente + CRM).

Modelagem baseada nas seções MEMÓRIA, ETAPAS DO CRM, DOCUMENTOS, GERAÇÃO DE
CONTRATOS, CONTROLE DE CUSTOS e PAINEL ADMINISTRATIVO do documento:

  * Lead          → cliente/potencial cliente e seus dados cadastrais.
  * Conversation  → um atendimento (thread) de um lead.
  * Message       → cada mensagem trocada (do cliente ou do agente).
  * Document      → arquivos enviados (CPF, RG, contratos, extratos...).
  * Contract      → contratos gerados para o lead.
  * Task          → tarefas/follow-ups do CRM.
  * Note          → anotações internas sobre o lead.
  * UsageLog      → controle de custos das requisições de IA.
  * AdminUser     → usuários do painel administrativo.

A memória é INDEPENDENTE do modelo de IA: guardamos qual provedor/modelo
respondeu apenas como metadado, mas o histórico em si é neutro.
"""

from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    Float,
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


class TaskStatus(str, enum.Enum):
    """Situação de uma tarefa/follow-up do CRM."""

    PENDENTE = "pendente"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"


class Lead(Base):
    """Cliente/lead e seus dados cadastrais (memória de longo prazo)."""

    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Identificação (o telefone do WhatsApp é a chave natural).
    phone: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cpf: Mapped[str | None] = mapped_column(String(20), nullable=True)
    rg: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    state: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Origem do lead (whatsapp, instagram, site, telegram...).
    channel: Mapped[str] = mapped_column(String(32), default="whatsapp")

    # Contexto do atendimento.
    problem: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[LeadStatus] = mapped_column(
        SAEnum(LeadStatus), default=LeadStatus.NOVO_LEAD, nullable=False, index=True
    )

    # Atendimento humano assumiu o controle? (painel administrativo)
    human_takeover: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_now, onupdate=_now
    )

    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="lead", cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(
        back_populates="lead", cascade="all, delete-orphan"
    )
    contracts: Mapped[list["Contract"]] = relationship(
        back_populates="lead", cascade="all, delete-orphan"
    )
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="lead", cascade="all, delete-orphan"
    )
    notes: Mapped[list["Note"]] = relationship(
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
    """Uma mensagem individual da conversa (do cliente, agente ou humano)."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), index=True
    )

    # "user" (cliente), "assistant" (agente) ou "system".
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


class Document(Base):
    """Arquivo enviado pelo cliente (CPF, RG, extrato, contrato, foto...).

    Conforme a seção DOCUMENTOS: armazenados e organizados por cliente, data
    e tipo. Aqui guardamos os metadados; o arquivo físico fica no disco
    (STORAGE_DIR), com o caminho referenciado em `path`.
    """

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lead_id: Mapped[int] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"), index=True
    )

    # Tipo lógico (cpf, rg, cnh, comprovante, contrato, extrato, foto...).
    doc_type: Mapped[str] = mapped_column(String(64), default="outro")
    filename: Mapped[str] = mapped_column(String(255))
    path: Mapped[str] = mapped_column(String(1000))
    content_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    lead: Mapped[Lead] = relationship(back_populates="documents")


class Contract(Base):
    """Contrato gerado para um lead (GERAÇÃO AUTOMÁTICA DE CONTRATOS)."""

    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lead_id: Mapped[int] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"), index=True
    )

    template: Mapped[str] = mapped_column(String(64), default="honorarios")
    object_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    fees: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pdf_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    signed: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    lead: Mapped[Lead] = relationship(back_populates="contracts")


class Task(Base):
    """Tarefa/follow-up do CRM (agenda, próxima ação)."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lead_id: Mapped[int] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"), index=True
    )

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        SAEnum(TaskStatus), default=TaskStatus.PENDENTE
    )
    due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    lead: Mapped[Lead] = relationship(back_populates="tasks")


class Note(Base):
    """Anotação interna sobre o lead (visível apenas no painel admin)."""

    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lead_id: Mapped[int] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"), index=True
    )
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    lead: Mapped[Lead] = relationship(back_populates="notes")


class UsageLog(Base):
    """Registro de uso da IA para CONTROLE DE CUSTOS (painel admin).

    Guarda, por requisição: modelo, provedor, tokens, custo estimado,
    latência, lead e conversa relacionados.
    """

    __tablename__ = "usage_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lead_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    conversation_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    provider: Mapped[str] = mapped_column(String(64))
    model: Mapped[str] = mapped_column(String(128))
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class AdminUser(Base):
    """Usuário do painel administrativo (autenticação JWT)."""

    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
