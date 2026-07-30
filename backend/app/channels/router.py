"""Rotas dos canais — webhook do WhatsApp Business API.

  * GET  /channels/whatsapp/webhook  → verificação do webhook (Meta).
  * POST /channels/whatsapp/webhook  → recebe mensagens e responde via IA.

O fluxo de resposta reutiliza o `memory_service` (mesma memória e mesmo
agente do canal genérico), provando que a lógica de atendimento é única e
independente do canal.
"""

from __future__ import annotations

from fastapi import APIRouter, Request, Response, status

from app.channels.whatsapp import whatsapp_client
from app.chat.prompts import SYSTEM_PROMPT
from app.core.exceptions import AllProvidersFailedError
from app.core.logging import get_logger
from app.memory.service import memory_service

logger = get_logger(__name__)

router = APIRouter(prefix="/channels", tags=["Canais"])


@router.get("/whatsapp/webhook")
async def whatsapp_verify(request: Request) -> Response:
    """Handshake de verificação do webhook exigido pela Meta."""
    params = request.query_params
    challenge = whatsapp_client.verify(
        params.get("hub.mode"),
        params.get("hub.verify_token"),
        params.get("hub.challenge"),
    )
    if challenge is not None:
        return Response(content=challenge, media_type="text/plain")
    return Response(status_code=status.HTTP_403_FORBIDDEN, content="Token inválido.")


@router.post("/whatsapp/webhook")
async def whatsapp_incoming(request: Request) -> dict:
    """Recebe mensagens do WhatsApp, gera a resposta da IA e a envia de volta.

    Sempre responde 200 rapidamente para a Meta não reenviar o evento; o
    processamento de cada mensagem é feito em sequência e os erros são
    tratados de forma isolada (uma mensagem com erro não derruba as demais).
    """
    # Valida a assinatura da Meta (segurança) antes de processar.
    raw_body = await request.body()
    if not whatsapp_client.verify_signature(
        raw_body, request.headers.get("X-Hub-Signature-256")
    ):
        logger.warning("Webhook do WhatsApp com assinatura inválida — ignorado.")
        return {"status": "invalid_signature"}

    payload = await request.json()
    incoming = whatsapp_client.parse_webhook(payload)

    for msg in incoming:
        try:
            response = await memory_service.handle_turn(
                msg.sender,
                msg.text,
                system=SYSTEM_PROMPT,
                name=msg.name,
                channel=msg.channel,
            )
        except AllProvidersFailedError:
            logger.error("IA indisponível para %s — enviando fallback.", msg.sender)
            await whatsapp_client.send_text(
                msg.sender,
                "Recebi sua mensagem e já retorno com todos os detalhes. "
                "Pode me contar um pouco mais sobre o seu caso?",
            )
            continue

        # Se um humano assumiu o atendimento, a resposta vem vazia — não envia.
        if response.content:
            await whatsapp_client.send_text(msg.sender, response.content)

    return {"status": "received", "processed": len(incoming)}
