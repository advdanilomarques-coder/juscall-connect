"""Ponto de entrada da aplicação (FastAPI).

Expõe a API HTTP. Nesta etapa temos:
  * GET  /                 → status da aplicação (healthcheck).
  * GET  /initial-message  → mensagem inicial obrigatória do atendimento.
  * POST /chat             → conversa COM MEMÓRIA (histórico persistido).

O banco de dados é inicializado automaticamente no startup (lifespan).

Executar em desenvolvimento:
    uvicorn app.main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.exceptions import AllProvidersFailedError
from app.core.logging import get_logger, setup_logging
from app.db.base import init_db
from app.memory.service import memory_service

# Configura os logs assim que o módulo é carregado.
setup_logging()
logger = get_logger(__name__)

# Personalidade + regras do agente (instrução de sistema).
SYSTEM_PROMPT = (
    "Você é a MARQUES IA, assistente virtual do escritório Marques Advogados "
    "Associados, especializado em Direito Bancário, Ações Revisionais, Busca e "
    "Apreensão de Veículos e Renegociação de Dívidas. Seja educada, humana, "
    "objetiva e persuasiva. Nunca revele que é uma inteligência artificial. "
    "Adapte a linguagem ao perfil do cliente."
)

# Mensagem inicial obrigatória (definida no documento do projeto).
INITIAL_MESSAGE = (
    "Olá! Seja muito bem-vindo(a) à Marques Advogados Associados. "
    "Meu nome é MARQUES IA. Sou a assistente virtual do escritório e estou "
    "aqui para ajudá-lo da melhor forma possível. Nosso atendimento é "
    "especializado em Direito Bancário, Ações Revisionais, Busca e Apreensão "
    "de Veículos e Renegociação de Dívidas. Conte, por favor, o que aconteceu "
    "para que eu possa entender seu caso e direcionar você da forma mais "
    "rápida possível."
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida da aplicação: cria as tabelas do banco no startup."""
    await init_db()
    logger.info("Aplicação iniciada: %s", settings.app_name)
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)


class ChatRequest(BaseModel):
    """Corpo da requisição do endpoint /chat."""

    phone: str = Field(..., description="Telefone do cliente (chave de memória).")
    message: str = Field(..., description="Mensagem enviada pelo cliente.")
    name: str | None = Field(default=None, description="Nome do cliente (opcional).")


class ChatResponse(BaseModel):
    """Corpo da resposta do endpoint /chat."""

    reply: str
    provider: str
    model: str


@app.get("/")
async def health() -> dict:
    """Healthcheck simples — confirma que a aplicação está no ar."""
    return {"app": settings.app_name, "env": settings.app_env, "status": "ok"}


@app.get("/initial-message")
async def initial_message() -> dict:
    """Retorna a mensagem inicial obrigatória do atendimento."""
    return {"message": INITIAL_MESSAGE}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Recebe uma mensagem do cliente e devolve a resposta do agente.

    Toda a conversa é persistida: o agente lembra do histórico do cliente
    (identificado pelo telefone) e continua de onde parou. O failover entre
    modelos é transparente e não afeta a memória.
    """
    try:
        response = await memory_service.handle_turn(
            request.phone,
            request.message,
            system=SYSTEM_PROMPT,
            name=request.name,
        )
    except AllProvidersFailedError:
        logger.error("Nenhum provedor de IA respondeu à mensagem do cliente.")
        # Resposta de fallback amigável — o cliente nunca vê um erro técnico.
        return ChatResponse(
            reply=(
                "Estou finalizando alguns detalhes do seu atendimento e já "
                "retorno. Pode me contar um pouco mais sobre o seu caso?"
            ),
            provider="fallback",
            model="none",
        )

    return ChatResponse(
        reply=response.content,
        provider=response.provider,
        model=response.model,
    )
