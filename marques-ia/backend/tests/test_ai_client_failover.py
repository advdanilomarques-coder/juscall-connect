# -*- coding: utf-8 -*-
"""Testa o failover do cliente de IA entre modelos gratuitos configurados."""
import asyncio
from unittest.mock import AsyncMock, patch

import httpx

from app.agent import ai_client


def test_usa_primeiro_modelo_quando_ele_funciona():
    async def fake_call(model, messages):
        return f"resposta de {model}"

    with patch("app.agent.ai_client._call_openrouter", new=AsyncMock(side_effect=fake_call)):
        texto, modelo = asyncio.run(ai_client.generate_reply([{"role": "user", "content": "oi"}]))

    assert modelo == ai_client.settings.OPENROUTER_MODELS_ORDER[0]
    assert "resposta de" in texto


def test_failover_para_o_proximo_modelo_quando_o_primeiro_falha():
    respostas = [httpx.RequestError("modelo indisponível"), "resposta ok"]

    async def fake_call(model, messages):
        resultado = respostas.pop(0)
        if isinstance(resultado, Exception):
            raise resultado
        return resultado

    with patch("app.agent.ai_client._call_openrouter", new=AsyncMock(side_effect=fake_call)):
        texto, modelo = asyncio.run(ai_client.generate_reply([{"role": "user", "content": "oi"}]))

    assert texto == "resposta ok"
    assert modelo == ai_client.settings.OPENROUTER_MODELS_ORDER[1]


def test_levanta_erro_quando_todos_os_modelos_falham():
    async def fake_call(model, messages):
        raise httpx.RequestError("sempre falha")

    with patch("app.agent.ai_client._call_openrouter", new=AsyncMock(side_effect=fake_call)):
        try:
            asyncio.run(ai_client.generate_reply([{"role": "user", "content": "oi"}]))
            assert False, "deveria ter levantado AIProviderError"
        except ai_client.AIProviderError:
            pass
