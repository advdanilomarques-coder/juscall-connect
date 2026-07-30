# -*- coding: utf-8 -*-
"""Testa se o agente reconhece corretamente cliente novo x cliente antigo/recorrente."""
import asyncio
from unittest.mock import AsyncMock, patch

from app.agent import service
from app.models.case import Caso
from app.models.client import Cliente
from app.models.message import Mensagem


def test_primeiro_contato_e_marcado_como_cliente_novo(db_session):
    with patch("app.agent.service.generate_reply", new=AsyncMock(return_value=("Olá!", "modelo-teste"))):
        resultado = asyncio.run(service.responder_cliente(
            db=db_session, telefone="5511999990001", user_message="Oi, preciso de ajuda",
        ))

    assert resultado["cliente_novo"] is True
    assert resultado["escalado_para_humano"] is False

    cliente = db_session.query(Cliente).filter(Cliente.telefone == "5511999990001").first()
    assert cliente is not None

    # Um caso deve ter sido criado automaticamente no funil (integração CRM).
    caso = db_session.query(Caso).filter(Caso.cliente_id == cliente.id).first()
    assert caso is not None
    assert caso.etapa_funil == "novo_lead"


def test_segundo_contato_e_reconhecido_como_cliente_antigo(db_session):
    with patch("app.agent.service.generate_reply", new=AsyncMock(return_value=("Olá!", "modelo-teste"))):
        asyncio.run(service.responder_cliente(
            db=db_session, telefone="5511999990002", user_message="Primeira mensagem",
        ))
        resultado_2 = asyncio.run(service.responder_cliente(
            db=db_session, telefone="5511999990002", user_message="Segunda mensagem",
        ))

    assert resultado_2["cliente_novo"] is False

    # Apenas um cliente deve existir para o mesmo telefone (sem duplicar).
    clientes = db_session.query(Cliente).filter(Cliente.telefone == "5511999990002").all()
    assert len(clientes) == 1

    # O histórico de mensagens deve conter as duas mensagens do usuário + duas respostas.
    mensagens = db_session.query(Mensagem).filter(Mensagem.cliente_id == clientes[0].id).all()
    assert len(mensagens) == 4


def test_escalona_para_humano_quando_ia_falha(db_session):
    with patch(
        "app.agent.service.generate_reply",
        new=AsyncMock(side_effect=service.AIProviderError("todos os modelos falharam")),
    ):
        resultado = asyncio.run(service.responder_cliente(
            db=db_session, telefone="5511999990003", user_message="Oi",
        ))

    assert resultado["escalado_para_humano"] is True
    assert resultado["modelo_utilizado"] is None
    assert resultado["texto"] == service.MENSAGEM_ESCALONAMENTO
