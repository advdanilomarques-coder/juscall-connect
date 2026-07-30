"""Rotas de atendimento (chat) genérico.

Expõe:
  * GET  /chat/initial-message → a mensagem inicial obrigatória.
  * POST /chat                 → conversa COM MEMÓRIA (histórico persistido).

Este é o canal "genérico" (site, widget, testes). Os canais específicos
(WhatsApp, Telegram...) têm seus próprios webhooks, mas todos reutilizam o
mesmo `memory_service` — a lógica de atendimento é única.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from app.chat.prompts import INITIAL_MESSAGE, SYSTEM_PROMPT
from app.core.exceptions import AllProvidersFailedError
from app.core.logging import get_logger
from app.deps import rate_limiter
from app.memory.service import memory_service

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["Atendimento"])


class ChatRequest(BaseModel):
    """Corpo da requisição do endpoint /chat."""

    phone: str = Field(..., description="Telefone do cliente (chave de memória).")
    message: str = Field(..., description="Mensagem enviada pelo cliente.")
    name: str | None = Field(default=None, description="Nome do cliente (opcional).")
    channel: str = Field(default="site", description="Canal de origem.")


class ChatResponse(BaseModel):
    """Corpo da resposta do endpoint /chat."""

    reply: str
    provider: str
    model: str


def _rate_limit(request: Request) -> None:
    """Aplica o rate limit por IP de origem (dependência leve)."""
    from fastapi import HTTPException, status

    client_ip = request.client.host if request.client else "unknown"
    if not rate_limiter.allow(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas requisições. Tente novamente em instantes.",
        )


@router.get("/initial-message")
async def initial_message() -> dict:
    """Retorna a mensagem inicial obrigatória do atendimento."""
    return {"message": INITIAL_MESSAGE}


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, _: None = Depends(_rate_limit)) -> ChatResponse:
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
            channel=request.channel,
        )
    except AllProvidersFailedError:
        logger.error("Nenhum provedor de IA respondeu à mensagem do cliente.")
        # Resposta de fallback amigável — o cliente nunca vê um erro técnico.
        return ChatResponse(
            reply=(
                "Estou finalizando alguns detalhes do seu atendimento e já "
                "retorno. Enquanto isso, pode me contar um pouco mais sobre o "
                "seu caso?"
            ),
            provider="fallback",
            model="none",
        )

    return ChatResponse(
        reply=response.content,
        provider=response.provider,
        model=response.model,
    )
