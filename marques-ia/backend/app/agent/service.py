# -*- coding: utf-8 -*-
"""
Camada de orquestração do agente:
  1. Identifica o cliente pelo telefone (cria se for a primeira vez).
  2. Carrega o histórico salvo (se o cliente já é conhecido).
  3. Monta o contexto e chama o cliente de IA (com failover).
  4. Persiste a mensagem do cliente e a resposta do agente.
  5. Escala para atendimento humano se todos os modelos de IA falharem.

Isso garante que o agente responda corretamente tanto clientes NOVOS
(primeiro contato) quanto clientes ANTIGOS/recorrentes (com memória contínua).
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.agent.ai_client import AIProviderError, generate_reply
from app.agent.prompts import build_messages
from app.models.case import Caso
from app.models.client import Cliente
from app.models.message import Mensagem
from app.rag.service import buscar_contexto

logger = logging.getLogger("marques_ia.agent.service")

MENSAGEM_ESCALONAMENTO = (
    "Recebemos sua mensagem e um de nossos advogados vai continuar o "
    "atendimento em instantes."
)

# Quantas mensagens anteriores (do cliente + do agente) carregar como contexto
# para clientes recorrentes.
HISTORICO_MAX_MENSAGENS = 20


def _obter_ou_criar_cliente(db: Session, telefone: str, client_name: Optional[str]) -> tuple[Cliente, bool]:
    """Retorna (cliente, cliente_novo). Cria o cliente se ele ainda não existir."""
    cliente = db.query(Cliente).filter(Cliente.telefone == telefone).first()

    if cliente is None:
        cliente = Cliente(telefone=telefone, nome=client_name)
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
        logger.info("Novo cliente cadastrado: %s", telefone)

        # Abre automaticamente um caso na primeira etapa do funil (CRM),
        # para que o atendimento já apareça no kanban do painel administrativo.
        caso_inicial = Caso(cliente_id=cliente.id, area_juridica="outro", etapa_funil="novo_lead")
        db.add(caso_inicial)
        db.commit()

        return cliente, True

    # Cliente recorrente: atualiza nome (se ainda não tinha) e último contato.
    if client_name and not cliente.nome:
        cliente.nome = client_name
    cliente.ultimo_contato_em = datetime.now(timezone.utc)
    db.commit()
    return cliente, False


def _carregar_historico(db: Session, cliente_id: int) -> list[dict]:
    """Carrega as últimas mensagens do cliente, em ordem cronológica."""
    mensagens = (
        db.query(Mensagem)
        .filter(Mensagem.cliente_id == cliente_id)
        .order_by(Mensagem.criado_em.desc())
        .limit(HISTORICO_MAX_MENSAGENS)
        .all()
    )
    mensagens.reverse()
    return [{"role": m.role, "content": m.conteudo} for m in mensagens]


def _salvar_mensagem(db: Session, cliente_id: int, role: str, conteudo: str) -> None:
    db.add(Mensagem(cliente_id=cliente_id, role=role, conteudo=conteudo))
    db.commit()


async def responder_cliente(
    db: Session,
    telefone: str,
    user_message: str,
    client_name: Optional[str] = None,
) -> dict:
    """
    Gera a resposta do agente para uma mensagem de cliente, identificando
    automaticamente se é um cliente novo ou um cliente antigo (pelo telefone).

    Retorna um dicionário com:
      - texto: resposta gerada (ou mensagem de escalonamento)
      - modelo_utilizado: nome do modelo que respondeu (ou None)
      - escalado_para_humano: True se todos os modelos de IA falharam
      - cliente_novo: True se este é o primeiro contato deste cliente
    """
    cliente, cliente_novo = _obter_ou_criar_cliente(db, telefone, client_name)
    history = [] if cliente_novo else _carregar_historico(db, cliente.id)

    area_juridica_atual = None
    if not cliente_novo:
        caso_recente = (
            db.query(Caso)
            .filter(Caso.cliente_id == cliente.id, Caso.status == "aberto")
            .order_by(Caso.atualizado_em.desc())
            .first()
        )
        if caso_recente and caso_recente.area_juridica != "outro":
            area_juridica_atual = caso_recente.area_juridica

    contexto_rag = buscar_contexto(db, consulta=user_message, area_juridica=area_juridica_atual, top_k=3)

    messages = build_messages(
        history=history,
        user_message=user_message,
        client_name=cliente.nome,
        cliente_novo=cliente_novo,
        contexto_rag=contexto_rag,
    )

    # Salva a mensagem do cliente antes de chamar a IA, garantindo que o
    # histórico não se perca mesmo se a chamada de IA falhar.
    _salvar_mensagem(db, cliente.id, role="user", conteudo=user_message)

    try:
        texto, modelo = await generate_reply(messages)
        escalado = False
    except AIProviderError as exc:
        logger.error("Escalonamento para humano (telefone %s): %s", telefone, exc)
        texto = MENSAGEM_ESCALONAMENTO
        modelo = None
        escalado = True

    _salvar_mensagem(db, cliente.id, role="assistant", conteudo=texto)

    return {
        "texto": texto,
        "modelo_utilizado": modelo,
        "escalado_para_humano": escalado,
        "cliente_novo": cliente_novo,
    }
