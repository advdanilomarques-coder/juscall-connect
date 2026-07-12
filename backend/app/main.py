"""Ponto de entrada da aplicação (FastAPI).

Expõe a API HTTP. Nesta primeira etapa temos:
  * GET  /            → status da aplicação (healthcheck).
  * POST /chat        → conversa com o agente Marques IA (via camada de IA).

As próximas etapas (webhook do WhatsApp, CRM, banco de dados) serão
adicionadas reutilizando exatamente a mesma camada de IA criada aqui.

Executar em desenvolvimento:
    uvicorn app.main:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from app.ai.manager import ai_manager
from app.ai.schemas import AIMessage, Role
from app.core.config import settings
from app.core.exceptions import AllProvidersFailedError
from app.core.logging import get_logger, setup_logging

# Configura os logs assim que o módulo é carregado.
setup_logging()
logger = get_logger(__name__)

# Personalidade + regras do agente. É a "instrução de sistema" que define
# quem é o agente. (Baseado na descrição do documento do projeto.)
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

app = FastAPI(title=settings.app_name, debug=settings.debug)


class ChatRequest(BaseModel):
    """Corpo da requisição do endpoint /chat."""

    message: str


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

    Toda a inteligência passa pela camada de abstração (`ai_manager`),
    que cuida sozinha do failover entre modelos.
    """
    messages = [AIMessage(role=Role.USER, content=request.message)]

    try:
        response = await ai_manager.generate(messages, system=SYSTEM_PROMPT)
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
