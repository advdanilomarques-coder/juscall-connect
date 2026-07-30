"""Serviço do CRM — regras de negócio de leads, funil, tarefas e anotações.

Não conhece HTTP: recebe uma sessão de banco e dados simples, e devolve
objetos do ORM. Isso mantém a lógica testável e reaproveitável (as rotas são
apenas uma "casca" fina sobre este serviço).
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Lead, LeadStatus, Note, Task, TaskStatus


class CRMService:
    """Operações do CRM sobre um único `AsyncSession`."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ----------------------------- Leads --------------------------------- #
    async def list_leads(
        self, *, status: LeadStatus | None = None, limit: int = 100, offset: int = 0
    ) -> list[Lead]:
        """Lista leads, opcionalmente filtrando por etapa do funil."""
        stmt = select(Lead).order_by(Lead.updated_at.desc())
        if status is not None:
            stmt = stmt.where(Lead.status == status)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_lead(self, lead_id: int) -> Lead | None:
        """Busca um lead pelo id."""
        return await self.session.get(Lead, lead_id)

    async def update_lead(self, lead: Lead, data: dict) -> Lead:
        """Aplica atualizações parciais nos dados cadastrais do lead."""
        for field, value in data.items():
            if value is not None and hasattr(lead, field):
                setattr(lead, field, value)
        await self.session.flush()
        return lead

    async def move_status(self, lead: Lead, status: LeadStatus) -> Lead:
        """Move o lead para outra etapa do funil (kanban)."""
        lead.status = status
        await self.session.flush()
        return lead

    async def set_takeover(self, lead: Lead, human: bool) -> Lead:
        """Liga/desliga o atendimento humano para este lead."""
        lead.human_takeover = human
        await self.session.flush()
        return lead

    async def kanban(self) -> dict[LeadStatus, list[Lead]]:
        """Agrupa todos os leads por etapa do funil (visão de kanban)."""
        result = await self.session.execute(
            select(Lead).order_by(Lead.updated_at.desc())
        )
        board: dict[LeadStatus, list[Lead]] = {s: [] for s in LeadStatus}
        for lead in result.scalars().all():
            board[lead.status].append(lead)
        return board

    async def funnel_counts(self) -> dict[str, int]:
        """Conta quantos leads existem em cada etapa (para gráficos/dashboard)."""
        result = await self.session.execute(
            select(Lead.status, func.count(Lead.id)).group_by(Lead.status)
        )
        counts = {s.value: 0 for s in LeadStatus}
        for status, total in result.all():
            counts[status.value] = total
        return counts

    # ----------------------------- Notas --------------------------------- #
    async def add_note(
        self, lead_id: int, content: str, *, author: str | None = None
    ) -> Note:
        note = Note(lead_id=lead_id, content=content, author=author)
        self.session.add(note)
        await self.session.flush()
        return note

    async def list_notes(self, lead_id: int) -> list[Note]:
        result = await self.session.execute(
            select(Note).where(Note.lead_id == lead_id).order_by(Note.id.desc())
        )
        return list(result.scalars().all())

    # ---------------------------- Tarefas -------------------------------- #
    async def add_task(self, lead_id: int, data: dict) -> Task:
        task = Task(lead_id=lead_id, **data)
        self.session.add(task)
        await self.session.flush()
        return task

    async def list_tasks(self, lead_id: int) -> list[Task]:
        result = await self.session.execute(
            select(Task).where(Task.lead_id == lead_id).order_by(Task.id.desc())
        )
        return list(result.scalars().all())

    async def update_task(self, task: Task, data: dict) -> Task:
        for field, value in data.items():
            if value is not None and hasattr(task, field):
                setattr(task, field, value)
        await self.session.flush()
        return task

    async def get_task(self, task_id: int) -> Task | None:
        return await self.session.get(Task, task_id)

    async def pending_tasks(self) -> list[Task]:
        """Todas as tarefas em aberto (agenda geral do escritório)."""
        result = await self.session.execute(
            select(Task)
            .where(Task.status.in_([TaskStatus.PENDENTE, TaskStatus.EM_ANDAMENTO]))
            .order_by(Task.due_at.is_(None), Task.due_at)
        )
        return list(result.scalars().all())
