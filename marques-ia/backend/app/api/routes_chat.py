# -*- coding: utf-8 -*-
"""Endpoint protegido para testar o agente de IA a partir do painel administrativo."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.agent.service import responder_cliente
from app.api.deps import get_current_admin
from app.core.rate_limit import permitir
from app.database.session import get_db
from app.models.user import AdminUser
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["agente de ia"])


@router.post("/testar", response_model=ChatResponse)
async def testar_agente(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """
    Testa o agente de IA (com failover entre modelos gratuitos) antes de
    conectar o número real do WhatsApp.

    O agente identifica automaticamente, pelo telefone informado, se o
    cliente é novo (primeiro contato) ou antigo/recorrente (já existe
    histórico salvo) e responde adequadamente em ambos os casos.
    """
    if not permitir(chave=f"chat_testar:{admin.email}", limite=30, janela_segundos=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Limite de requisições de teste excedido. Aguarde um instante.",
        )

    resultado = await responder_cliente(
        db=db,
        telefone=payload.telefone,
        user_message=payload.mensagem,
        client_name=payload.nome_cliente,
    )
    return resultado
