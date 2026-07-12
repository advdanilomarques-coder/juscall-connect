"""Testes da camada de IA — foco no comportamento de FAILOVER.

Usamos provedores "falsos" (fakes) para testar a lógica do gerenciador SEM
gastar tokens nem depender de rede. Isso comprova que a abstração funciona:
o gerenciador não sabe (nem precisa saber) qual modelo real está por trás.
"""

from __future__ import annotations

import pytest

from app.ai.base import AIProvider
from app.ai.manager import AIManager
from app.ai.schemas import AIMessage, AIResponse, Role
from app.core.exceptions import AIProviderError, AllProvidersFailedError


class _FakeOkProvider(AIProvider):
    """Provedor falso que sempre responde com sucesso."""

    name = "fake_ok"

    async def generate(self, messages, *, system=None, max_tokens=1024) -> AIResponse:
        return AIResponse(content="ok", provider=self.name, model="fake-1")

    def is_available(self) -> bool:
        return True


class _FakeFailProvider(AIProvider):
    """Provedor falso que sempre falha (simula indisponibilidade)."""

    name = "fake_fail"

    async def generate(self, messages, *, system=None, max_tokens=1024) -> AIResponse:
        raise AIProviderError("simulação de falha")

    def is_available(self) -> bool:
        return True


def _manager_with(providers: list[AIProvider]) -> AIManager:
    """Cria um AIManager e injeta provedores de teste."""
    manager = AIManager()
    manager._providers = providers  # noqa: SLF001 (injeção só para teste)
    return manager


@pytest.mark.asyncio
async def test_usa_primeiro_provedor_quando_ok() -> None:
    manager = _manager_with([_FakeOkProvider(), _FakeFailProvider()])
    resp = await manager.generate([AIMessage(role=Role.USER, content="oi")])
    assert resp.provider == "fake_ok"


@pytest.mark.asyncio
async def test_failover_quando_primeiro_falha() -> None:
    # O primeiro falha, então o gerenciador deve alternar para o segundo.
    manager = _manager_with([_FakeFailProvider(), _FakeOkProvider()])
    resp = await manager.generate([AIMessage(role=Role.USER, content="oi")])
    assert resp.provider == "fake_ok"


@pytest.mark.asyncio
async def test_erro_quando_todos_falham() -> None:
    manager = _manager_with([_FakeFailProvider(), _FakeFailProvider()])
    with pytest.raises(AllProvidersFailedError):
        await manager.generate([AIMessage(role=Role.USER, content="oi")])
