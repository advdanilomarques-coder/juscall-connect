"""Testes da camada de memória.

Comprovam que o histórico é persistido e reaproveitado entre turnos, SEM
gastar tokens (usamos um gerenciador de IA falso) e usando um banco SQLite
temporário e isolado por teste.
"""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.ai.schemas import AIMessage, AIResponse
from app.db.base import Base
from app.db.models import LeadStatus, UsageLog
from app.memory.repository import ConversationRepository
from app.memory.service import MemoryService
from sqlalchemy import func, select


class _FakeManager:
    """Gerenciador de IA falso: registra o contexto recebido e responde fixo."""

    def __init__(self) -> None:
        self.last_messages: list[AIMessage] | None = None

    async def generate(self, messages, *, system=None, max_tokens=None, task=None) -> AIResponse:
        self.last_messages = messages
        return AIResponse(
            content="resposta do agente",
            provider="fake",
            model="fake-1",
            input_tokens=10,
            output_tokens=5,
            cost_usd=0.0001,
            latency_ms=42,
        )


@pytest.fixture
async def session_factory(tmp_path):
    """Cria um banco SQLite temporário com as tabelas já criadas."""
    url = f"sqlite+aiosqlite:///{tmp_path}/test.db"
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


async def test_memoria_persiste_e_cresce(session_factory) -> None:
    fake = _FakeManager()
    service = MemoryService(session_factory=session_factory, manager=fake)

    # 1º turno: o contexto enviado à IA tem apenas a mensagem atual.
    await service.handle_turn("5511999999999", "Meu carro foi apreendido")
    assert fake.last_messages is not None
    assert len(fake.last_messages) == 1

    # 2º turno: agora o contexto inclui user1 + assistant1 + user2 = 3.
    await service.handle_turn("5511999999999", "E agora, o que faço?")
    assert len(fake.last_messages) == 3

    # No banco: 2 mensagens do cliente + 2 do agente = 4.
    async with session_factory() as session:
        repo = ConversationRepository(session)
        lead = await repo.get_or_create_lead("5511999999999")
        conversation = await repo.get_or_create_conversation(lead)
        messages = await repo.get_messages(conversation.id)

    assert len(messages) == 4
    # O status do lead avançou no funil após o primeiro atendimento.
    assert lead.status == LeadStatus.PRIMEIRO_ATENDIMENTO


async def test_registra_uso_para_controle_de_custos(session_factory) -> None:
    fake = _FakeManager()
    service = MemoryService(session_factory=session_factory, manager=fake)
    await service.handle_turn("5511888888888", "Olá")

    async with session_factory() as session:
        total = await session.scalar(select(func.count(UsageLog.id)))
        cost = await session.scalar(select(func.sum(UsageLog.cost_usd)))

    assert total == 1
    assert cost == pytest.approx(0.0001)


async def test_leads_diferentes_nao_compartilham_memoria(session_factory) -> None:
    fake = _FakeManager()
    service = MemoryService(session_factory=session_factory, manager=fake)

    await service.handle_turn("5511111111111", "Olá")
    await service.handle_turn("5522222222222", "Oi")

    # O segundo cliente é novo: seu contexto tem só a própria mensagem.
    assert len(fake.last_messages) == 1
