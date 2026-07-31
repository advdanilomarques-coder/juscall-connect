# -*- coding: utf-8 -*-
"""
Webhook do WhatsApp Business Cloud API.

- GET  /webhook/whatsapp  -> verificação exigida pela Meta ao cadastrar o webhook.
- POST /webhook/whatsapp  -> recebimento de mensagens reais dos clientes.

Segurança: toda requisição POST tem sua assinatura HMAC (X-Hub-Signature-256)
validada contra WHATSAPP_APP_SECRET antes de qualquer processamento, e o
telefone de origem é limitado por rate limiting para evitar abuso.
"""
import hashlib
import hmac
import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.agent.service import responder_cliente
from app.core.audit import registrar_log
from app.core.config import settings
from app.core.rate_limit import permitir
from app.database.session import get_db
from app.integrations.transcription import TranscricaoError, transcrever_audio
from app.integrations.whatsapp_client import baixar_midia, enviar_mensagem_texto

router = APIRouter(prefix="/webhook/whatsapp", tags=["whatsapp"])
logger = logging.getLogger("marques_ia.whatsapp.webhook")

TIPOS_NAO_TEXTO_SUPORTADOS = {"audio", "image", "document", "video", "sticker", "location"}

MENSAGEM_TIPO_NAO_SUPORTADO = (
    "Recebemos seu arquivo, mas por enquanto só conseguimos processar mensagens em texto. "
    "Pode descrever em poucas palavras o que você precisa? Se preferir, um de nossos "
    "advogados também pode dar continuidade."
)

MENSAGEM_AUDIO_FALHOU = (
    "Não consegui ouvir seu áudio agora. Pode me enviar em texto o que você precisa?"
)

MENSAGEM_LIMITE_EXCEDIDO = (
    "Recebemos várias mensagens em pouco tempo. Um de nossos advogados vai revisar a "
    "conversa e responder em breve."
)


@router.get("")
def verificar_webhook(
    hub_mode: str = Query(default=None, alias="hub.mode"),
    hub_verify_token: str = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str = Query(default=None, alias="hub.challenge"),
):
    """
    Endpoint de verificação chamado pela Meta ao salvar a configuração do
    webhook. Deve responder com o valor de 'hub.challenge' em texto puro,
    apenas se o token enviado bater com WHATSAPP_VERIFY_TOKEN.
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook do WhatsApp verificado com sucesso.")
        return Response(content=hub_challenge or "", media_type="text/plain")

    logger.warning("Falha na verificação do webhook do WhatsApp (token não confere).")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token de verificação inválido")


def _validar_assinatura(corpo_bruto: bytes, assinatura_header: Optional[str]) -> bool:
    """
    Valida o cabeçalho X-Hub-Signature-256 enviado pela Meta, comparando com
    o HMAC-SHA256 do corpo bruto usando WHATSAPP_APP_SECRET.

    Se WHATSAPP_APP_SECRET não estiver configurado, a validação é pulada
    (com aviso em log) — útil apenas para testes locais rápidos; em
    produção, o App Secret deve sempre estar preenchido no .env.
    """
    if not settings.WHATSAPP_APP_SECRET:
        logger.warning(
            "WHATSAPP_APP_SECRET não configurado — validação de assinatura do "
            "webhook está DESATIVADA. Configure antes de ir para produção."
        )
        return True

    if not assinatura_header or not assinatura_header.startswith("sha256="):
        return False

    assinatura_esperada = hmac.new(
        settings.WHATSAPP_APP_SECRET.encode("utf-8"), corpo_bruto, hashlib.sha256
    ).hexdigest()
    assinatura_recebida = assinatura_header.split("=", 1)[1]

    return hmac.compare_digest(assinatura_esperada, assinatura_recebida)


def _extrair_mensagem(payload: dict) -> Optional[dict]:
    """
    Extrai os dados da mensagem do payload padrão da Cloud API. Retorna um dict
    com telefone, texto, nome, tipo e media_id — ou None se o payload não contiver
    uma mensagem nova relevante (ex.: evento de status como 'entregue' ou 'lido').
    """
    try:
        value = payload["entry"][0]["changes"][0]["value"]
        mensagens = value.get("messages")
        if not mensagens:
            return None

        mensagem = mensagens[0]
        tipo = mensagem.get("type")
        telefone = mensagem["from"]

        nome_cliente = None
        contatos = value.get("contacts") or []
        if contatos:
            nome_cliente = contatos[0].get("profile", {}).get("name")

        base = {"telefone": telefone, "nome": nome_cliente, "tipo": tipo, "texto": None, "media_id": None}

        if tipo == "text":
            base["texto"] = mensagem["text"]["body"]
            return base

        if tipo == "audio":
            base["media_id"] = (mensagem.get("audio") or {}).get("id")
            return base

        if tipo in TIPOS_NAO_TEXTO_SUPORTADOS:
            return base

        return None
    except (KeyError, IndexError, TypeError) as exc:
        logger.warning("Payload do webhook em formato inesperado: %s", exc)
        return None


@router.post("")
async def receber_mensagem(request: Request, db: Session = Depends(get_db)):
    """
    Recebe mensagens do WhatsApp, gera a resposta do agente (reconhecendo
    automaticamente cliente novo ou antigo) e envia a resposta de volta.
    """
    corpo_bruto = await request.body()
    assinatura = request.headers.get("X-Hub-Signature-256")

    if not _validar_assinatura(corpo_bruto, assinatura):
        logger.warning("Assinatura do webhook inválida — requisição rejeitada.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Assinatura inválida")

    payload = json.loads(corpo_bruto or b"{}")
    extraido = _extrair_mensagem(payload)

    if extraido is None:
        # Evento irrelevante para o agente (ex.: confirmação de leitura).
        return {"status": "ignorado"}

    telefone = extraido["telefone"]
    nome_cliente = extraido["nome"]
    tipo = extraido["tipo"]
    texto_recebido = extraido["texto"]

    if not permitir(chave=f"whatsapp:{telefone}", limite=20, janela_segundos=60):
        logger.warning("Rate limit excedido para o telefone %s", telefone)
        await enviar_mensagem_texto(telefone_destino=telefone, texto=MENSAGEM_LIMITE_EXCEDIDO)
        registrar_log(db, acao="rate_limit_excedido", entidade="whatsapp", detalhes=telefone)
        return {"status": "limite_excedido"}

    # Áudio de voz: baixa o arquivo do WhatsApp e transcreve para texto.
    if tipo == "audio":
        if not settings.TRANSCRICAO_HABILITADA or not extraido["media_id"]:
            await enviar_mensagem_texto(telefone_destino=telefone, texto=MENSAGEM_TIPO_NAO_SUPORTADO)
            return {"status": "audio_sem_transcricao"}
        try:
            audio_bytes = await baixar_midia(extraido["media_id"])
            texto_recebido = await transcrever_audio(audio_bytes)
            logger.info("Áudio de %s transcrito com sucesso.", telefone)
        except (TranscricaoError, Exception) as exc:  # noqa: BLE001 — degrada com segurança
            logger.error("Falha ao processar áudio de %s: %s", telefone, exc)
            await enviar_mensagem_texto(telefone_destino=telefone, texto=MENSAGEM_AUDIO_FALHOU)
            return {"status": "audio_falhou"}
    elif tipo != "text":
        await enviar_mensagem_texto(telefone_destino=telefone, texto=MENSAGEM_TIPO_NAO_SUPORTADO)
        logger.info("Mensagem não textual recebida de %s — resposta padrão enviada.", telefone)
        return {"status": "tipo_nao_suportado"}

    if not texto_recebido:
        await enviar_mensagem_texto(telefone_destino=telefone, texto=MENSAGEM_TIPO_NAO_SUPORTADO)
        return {"status": "sem_texto"}

    resultado = await responder_cliente(
        db=db,
        telefone=telefone,
        user_message=texto_recebido,
        client_name=nome_cliente,
    )

    await enviar_mensagem_texto(telefone_destino=telefone, texto=resultado["texto"])

    if resultado["escalado_para_humano"]:
        registrar_log(db, acao="escalado_para_humano", entidade="cliente", detalhes=telefone)

    return {"status": "ok", "cliente_novo": resultado["cliente_novo"]}
