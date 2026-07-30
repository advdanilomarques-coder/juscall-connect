"""Testes da camada de IA — foco em FAILOVER, RETRY e ROTEAMENTO.

Usamos provedores "falsos" (fakes) para testar a lógica do gerenciador SEM
gastar tokens nem depender de rede. Isso comprova que a abstração funciona:
o gerenciador não sabe (nem precisa saber) qual modelo real está por trás.
"""

from __future__ import annotations

import pytest

from app.ai.base import AIProvider
from app.ai.manager import AIManager
from app.ai.schemas import AIMessage, AIResponse, Role, TaskType
from app.core.exceptions import AIProviderError, AllProvidersFailedError


class _FakeOkProvider(AIProvider):
    """Provedor falso que sempre responde com sucesso."""

    def __init__(self, name: str = "fake_ok") -> None:
        self.name = name
        self.calls = 0

    async def generate(self, messages, *, system=None, max_tokens=1024) -> AIResponse:
        self.calls += 1
        return AIResponse(content="ok", provider=self.name, model="fake-1")

    def is_available(self) -> bool:
        return True


class _FakeFailProvider(AIProvider):
    """Provedor falso que sempre falha (simula indisponibilidade)."""

    def __init__(self, name: str = "fake_fail") -> None:
        self.name = name
        self.calls = 0

    async def generate(self, messages, *, system=None, max_tokens=1024) -> AIResponse:
        self.calls += 1
        raise AIProviderError("simulação de falha")

    def is_available(self) -> bool:
        return True


def _manager_with(providers: list[AIProvider], routing=None) -> AIManager:
    """Cria um AIManager e injeta provedores/roteamento de teste."""
    manager = AIManager()
    manager._providers = providers  # noqa: SLF001 (injeção só para teste)
    manager._by_name = {p.name: p for p in providers}  # noqa: SLF001
    manager._task_routing = routing or {}  # noqa: SLF001
    return manager


async def test_usa_primeiro_provedor_quando_ok() -> None:
    manager = _manager_with([_FakeOkProvider(), _FakeFailProvider()])
    resp = await manager.generate([AIMessage(role=Role.USER, content="oi")])
    assert resp.provider == "fake_ok"


async def test_failover_quando_primeiro_falha() -> None:
    # O primeiro falha, então o gerenciador deve alternar para o segundo.
    manager = _manager_with([_FakeFailProvider(), _FakeOkProvider()])
    resp = await manager.generate([AIMessage(role=Role.USER, content="oi")])
    assert resp.provider == "fake_ok"


async def test_erro_quando_todos_falham() -> None:
    manager = _manager_with([_FakeFailProvider("f1"), _FakeFailProvider("f2")])
    with pytest.raises(AllProvidersFailedError):
        await manager.generate([AIMessage(role=Role.USER, content="oi")])


async def test_retry_antes_do_failover(monkeypatch) -> None:
    # Com AI_MAX_RETRIES=2, um provedor que falha é chamado 2x antes do failover.
    from app.core.config import settings

    monkeypatch.setattr(settings, "ai_max_retries", 2)
    monkeypatch.setattr(settings, "ai_retry_backoff", 0.0)  # sem espera no teste
    fail = _FakeFailProvider()
    ok = _FakeOkProvider()
    manager = _manager_with([fail, ok])
    resp = await manager.generate([AIMessage(role=Role.USER, content="oi")])
    assert resp.provider == "fake_ok"
    assert fail.calls == 2  # tentou 2 vezes antes de desistir


async def test_roteamento_por_tarefa_prioriza_provedor() -> None:
    # A tarefa 'analise_juridica' deve priorizar o provedor 'especialista',
    # mesmo ele estando por último na ordem.
    generico = _FakeOkProvider("generico")
    especialista = _FakeOkProvider("especialista")
    manager = _manager_with(
        [generico, especialista],
        routing={"analise_juridica": "especialista"},
    )
    resp = await manager.generate(
        [AIMessage(role=Role.USER, content="analise")],
        task=TaskType.ANALISE_JURIDICA,
    )
    assert resp.provider == "especialista"
    assert especialista.calls == 1
    assert generico.calls == 0
