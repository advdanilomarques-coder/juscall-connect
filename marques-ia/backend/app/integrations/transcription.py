# -*- coding: utf-8 -*-
"""
Transcrição de áudio de voz (ex.: áudios do WhatsApp) para texto, usando um
serviço compatível com a API de transcrição da OpenAI (Whisper).

Padrão: Groq (https://console.groq.com) — tem plano gratuito e usa o modelo
whisper-large-v3-turbo. Para usar a OpenAI, basta trocar TRANSCRICAO_BASE_URL,
TRANSCRICAO_MODELO e TRANSCRICAO_API_KEY no .env.

Se TRANSCRICAO_API_KEY não estiver configurada, transcrever_audio levanta
TranscricaoError e o chamador deve tratar com uma resposta padrão pedindo texto.
"""
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger("marques_ia.transcricao")


class TranscricaoError(Exception):
    """Falha ao transcrever um áudio (serviço indisponível ou não configurado)."""


async def transcrever_audio(audio_bytes: bytes, nome_arquivo: str = "audio.ogg") -> str:
    """
    Envia o áudio para o serviço de transcrição e retorna o texto reconhecido.

    Levanta TranscricaoError se o recurso não estiver configurado ou se a
    chamada falhar — para que o webhook possa responder pedindo uma mensagem
    de texto, sem quebrar o atendimento.
    """
    if not settings.TRANSCRICAO_HABILITADA:
        raise TranscricaoError("Transcrição de áudio não configurada (TRANSCRICAO_API_KEY vazia).")

    url = f"{settings.TRANSCRICAO_BASE_URL}/audio/transcriptions"
    headers = {"Authorization": f"Bearer {settings.TRANSCRICAO_API_KEY}"}
    files = {"file": (nome_arquivo, audio_bytes, "application/octet-stream")}
    data = {"model": settings.TRANSCRICAO_MODELO, "language": "pt"}

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resposta = await client.post(url, headers=headers, files=files, data=data)
        resposta.raise_for_status()
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        logger.error("Falha na transcrição de áudio: %s", exc)
        raise TranscricaoError(str(exc)) from exc

    texto = (resposta.json().get("text") or "").strip()
    if not texto:
        raise TranscricaoError("Transcrição retornou vazia.")

    logger.info("Áudio transcrito com sucesso (%d caracteres).", len(texto))
    return texto
