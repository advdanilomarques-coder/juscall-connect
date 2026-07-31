# -*- coding: utf-8 -*-
"""
Cliente HTTP para envio de mensagens via WhatsApp Business Cloud API (Meta).
"""
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger("marques_ia.whatsapp")

GRAPH_API_VERSION = "v20.0"


async def enviar_mensagem_texto(telefone_destino: str, texto: str) -> bool:
    """
    Envia uma mensagem de texto simples para o telefone informado.
    Retorna True se o envio foi aceito pela API da Meta, False caso contrário.
    """
    url = (
        f"https://graph.facebook.com/{GRAPH_API_VERSION}/"
        f"{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    )
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": telefone_destino,
        "type": "text",
        "text": {"body": texto},
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(url, headers=headers, json=payload)

    if response.status_code >= 400:
        logger.error(
            "Falha ao enviar mensagem WhatsApp para %s (HTTP %s): %s",
            telefone_destino, response.status_code, response.text,
        )
        return False

    logger.info("Mensagem enviada com sucesso ao WhatsApp: %s", telefone_destino)
    return True


async def baixar_midia(media_id: str) -> bytes:
    """
    Baixa um arquivo de mídia (ex.: áudio de voz) do WhatsApp a partir do seu
    media_id. É um processo em duas etapas exigido pela Cloud API:
      1) consulta a URL temporária do arquivo pelo media_id;
      2) baixa o conteúdo dessa URL (ambas autenticadas com o WHATSAPP_TOKEN).

    Retorna os bytes do arquivo. Levanta httpx.HTTPError em caso de falha.
    """
    headers = {"Authorization": f"Bearer {settings.WHATSAPP_TOKEN}"}

    async with httpx.AsyncClient(timeout=30.0) as client:
        meta = await client.get(
            f"https://graph.facebook.com/{GRAPH_API_VERSION}/{media_id}", headers=headers
        )
        meta.raise_for_status()
        url_arquivo = meta.json()["url"]

        arquivo = await client.get(url_arquivo, headers=headers)
        arquivo.raise_for_status()
        return arquivo.content
