"""Schemas (Pydantic) de entrada/saída do CRM.

Separar os schemas da API dos modelos do banco (ORM) é boa prática: a API
expõe só o que precisa, com validação, sem vazar detalhes internos do banco.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.models import LeadStatus, TaskStatus


class LeadOut(BaseModel):
    """Representação de um lead para o painel."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    phone: str
    name: str | None
    cpf: str | None
    email: str | None
    city: str | None
    state: str | None
    channel: str
    problem: str | None
    status: LeadStatus
    human_takeover: bool
    created_at: datetime
    updated_at: datetime


class LeadUpdate(BaseModel):
    """Campos editáveis de um lead (todos opcionais)."""

    name: str | None = None
    cpf: str | None = None
    rg: str | None = None
    email: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    problem: str | None = None


class StatusUpdate(BaseModel):
    """Mudança de etapa no funil (mover card no kanban)."""

    status: LeadStatus


class TakeoverUpdate(BaseModel):
    """Liga/desliga o atendimento humano (silencia/reativa o agente)."""

    human_takeover: bool


class NoteIn(BaseModel):
    content: str = Field(..., min_length=1)
    author: str | None = None


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author: str | None
    content: str
    created_at: datetime


class TaskIn(BaseModel):
    title: str = Field(..., min_length=1)
    description: str | None = None
    due_at: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    due_at: datetime | None = None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TaskStatus
    due_at: datetime | None
    created_at: datetime


class KanbanColumn(BaseModel):
    """Uma coluna do kanban: uma etapa do funil e seus leads."""

    status: LeadStatus
    leads: list[LeadOut]
