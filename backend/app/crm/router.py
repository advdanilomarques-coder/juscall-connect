"""Rotas do CRM (painel administrativo — protegidas por JWT).

Todas as rotas exigem um administrador autenticado (`get_current_admin`).
São a interface entre o front-end do CRM (kanban, funil, cadastros) e a
lógica de negócio do `CRMService`.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crm.schemas import (
    KanbanColumn,
    LeadOut,
    LeadUpdate,
    NoteIn,
    NoteOut,
    StatusUpdate,
    TakeoverUpdate,
    TaskIn,
    TaskOut,
    TaskUpdate,
)
from app.crm.service import CRMService
from app.db.models import AdminUser, LeadStatus
from app.deps import get_current_admin, get_session

router = APIRouter(
    prefix="/crm",
    tags=["CRM"],
    dependencies=[Depends(get_current_admin)],  # protege TODAS as rotas do CRM
)


async def _get_lead_or_404(service: CRMService, lead_id: int):
    lead = await service.get_lead(lead_id)
    if lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead não encontrado."
        )
    return lead


@router.get("/leads", response_model=list[LeadOut])
async def list_leads(
    status_filter: LeadStatus | None = None,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
) -> list[LeadOut]:
    """Lista os leads, opcionalmente filtrando por etapa do funil."""
    leads = await CRMService(session).list_leads(
        status=status_filter, limit=limit, offset=offset
    )
    return [LeadOut.model_validate(lead) for lead in leads]


@router.get("/kanban", response_model=list[KanbanColumn])
async def kanban(session: AsyncSession = Depends(get_session)) -> list[KanbanColumn]:
    """Retorna o quadro kanban: cada etapa do funil com seus leads."""
    board = await CRMService(session).kanban()
    return [
        KanbanColumn(
            status=st, leads=[LeadOut.model_validate(l) for l in leads]
        )
        for st, leads in board.items()
    ]


@router.get("/funnel")
async def funnel(session: AsyncSession = Depends(get_session)) -> dict[str, int]:
    """Contagem de leads por etapa do funil (para gráficos do dashboard)."""
    return await CRMService(session).funnel_counts()


@router.get("/leads/{lead_id}", response_model=LeadOut)
async def get_lead(
    lead_id: int, session: AsyncSession = Depends(get_session)
) -> LeadOut:
    service = CRMService(session)
    lead = await _get_lead_or_404(service, lead_id)
    return LeadOut.model_validate(lead)


@router.patch("/leads/{lead_id}", response_model=LeadOut)
async def update_lead(
    lead_id: int,
    data: LeadUpdate,
    session: AsyncSession = Depends(get_session),
) -> LeadOut:
    service = CRMService(session)
    lead = await _get_lead_or_404(service, lead_id)
    lead = await service.update_lead(lead, data.model_dump(exclude_unset=True))
    await session.commit()
    return LeadOut.model_validate(lead)


@router.patch("/leads/{lead_id}/status", response_model=LeadOut)
async def move_status(
    lead_id: int,
    data: StatusUpdate,
    session: AsyncSession = Depends(get_session),
) -> LeadOut:
    """Move o lead para outra etapa do funil (arrastar card no kanban)."""
    service = CRMService(session)
    lead = await _get_lead_or_404(service, lead_id)
    lead = await service.move_status(lead, data.status)
    await session.commit()
    return LeadOut.model_validate(lead)


@router.patch("/leads/{lead_id}/takeover", response_model=LeadOut)
async def set_takeover(
    lead_id: int,
    data: TakeoverUpdate,
    session: AsyncSession = Depends(get_session),
) -> LeadOut:
    """Assume/devolve o atendimento humano (silencia/reativa o agente)."""
    service = CRMService(session)
    lead = await _get_lead_or_404(service, lead_id)
    lead = await service.set_takeover(lead, data.human_takeover)
    await session.commit()
    return LeadOut.model_validate(lead)


# ------------------------------- Notas ----------------------------------- #
@router.get("/leads/{lead_id}/notes", response_model=list[NoteOut])
async def list_notes(
    lead_id: int, session: AsyncSession = Depends(get_session)
) -> list[NoteOut]:
    notes = await CRMService(session).list_notes(lead_id)
    return [NoteOut.model_validate(n) for n in notes]


@router.post("/leads/{lead_id}/notes", response_model=NoteOut, status_code=201)
async def add_note(
    lead_id: int,
    data: NoteIn,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
) -> NoteOut:
    service = CRMService(session)
    await _get_lead_or_404(service, lead_id)
    note = await service.add_note(
        lead_id, data.content, author=data.author or admin.email
    )
    await session.commit()
    return NoteOut.model_validate(note)


# ------------------------------ Tarefas ---------------------------------- #
@router.get("/leads/{lead_id}/tasks", response_model=list[TaskOut])
async def list_tasks(
    lead_id: int, session: AsyncSession = Depends(get_session)
) -> list[TaskOut]:
    tasks = await CRMService(session).list_tasks(lead_id)
    return [TaskOut.model_validate(t) for t in tasks]


@router.post("/leads/{lead_id}/tasks", response_model=TaskOut, status_code=201)
async def add_task(
    lead_id: int,
    data: TaskIn,
    session: AsyncSession = Depends(get_session),
) -> TaskOut:
    service = CRMService(session)
    await _get_lead_or_404(service, lead_id)
    task = await service.add_task(lead_id, data.model_dump(exclude_unset=True))
    await session.commit()
    return TaskOut.model_validate(task)


@router.patch("/tasks/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    session: AsyncSession = Depends(get_session),
) -> TaskOut:
    service = CRMService(session)
    task = await service.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
    task = await service.update_task(task, data.model_dump(exclude_unset=True))
    await session.commit()
    return TaskOut.model_validate(task)
