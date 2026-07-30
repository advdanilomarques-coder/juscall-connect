"""Testes do CRM — funil, kanban, notas e tarefas.

Usam um banco SQLite temporário e isolado por teste, exercitando a lógica de
negócio do CRMService diretamente (sem HTTP).
"""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.crm.service import CRMService
from app.db.base import Base
from app.db.models import Lead, LeadStatus, TaskStatus


@pytest.fixture
async def session_factory(tmp_path):
    url = f"sqlite+aiosqlite:///{tmp_path}/crm.db"
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


async def _make_lead(session, phone: str) -> Lead:
    lead = Lead(phone=phone, name="Cliente Teste")
    session.add(lead)
    await session.flush()
    return lead


async def test_mover_status_no_funil(session_factory) -> None:
    async with session_factory() as session:
        crm = CRMService(session)
        lead = await _make_lead(session, "5511000000001")
        assert lead.status == LeadStatus.NOVO_LEAD

        await crm.move_status(lead, LeadStatus.ANALISE_JURIDICA)
        await session.commit()
        assert lead.status == LeadStatus.ANALISE_JURIDICA


async def test_kanban_agrupa_por_etapa(session_factory) -> None:
    async with session_factory() as session:
        crm = CRMService(session)
        l1 = await _make_lead(session, "5511000000002")
        l2 = await _make_lead(session, "5511000000003")
        await crm.move_status(l2, LeadStatus.CONTRATO_ENVIADO)
        await session.commit()

        board = await crm.kanban()
        assert l1 in board[LeadStatus.NOVO_LEAD]
        assert l2 in board[LeadStatus.CONTRATO_ENVIADO]
        # Todas as etapas existem como colunas, mesmo vazias.
        assert set(board.keys()) == set(LeadStatus)


async def test_notas_e_tarefas(session_factory) -> None:
    async with session_factory() as session:
        crm = CRMService(session)
        lead = await _make_lead(session, "5511000000004")
        await session.commit()

        await crm.add_note(lead.id, "Cliente prefere contato à tarde.", author="admin")
        note_list = await crm.list_notes(lead.id)
        assert len(note_list) == 1

        task = await crm.add_task(lead.id, {"title": "Ligar para o cliente"})
        assert task.status == TaskStatus.PENDENTE

        await crm.update_task(task, {"status": TaskStatus.CONCLUIDA})
        await session.commit()
        assert task.status == TaskStatus.CONCLUIDA
