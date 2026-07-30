# -*- coding: utf-8 -*-
"""
Envio de e-mails via SMTP (biblioteca padrão do Python — nenhuma dependência
extra necessária). Usado para mandar automaticamente o contrato aprovado, em
PDF, para o e-mail do cliente, e para notificações do escritório.

Se o SMTP não estiver configurado no .env (SMTP_HOST em branco), as funções
apenas registram um aviso e retornam False, sem quebrar o resto do sistema.
"""
import logging
import mimetypes
import os
import smtplib
import ssl
from email.message import EmailMessage
from typing import Iterable, Optional

from app.core.config import settings

logger = logging.getLogger("marques_ia.email")


class EmailError(Exception):
    """Falha ao enviar um e-mail (conexão, autenticação ou envio)."""


def _remetente() -> str:
    endereco = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
    nome = settings.SMTP_FROM_NAME or settings.APP_NAME
    return f"{nome} <{endereco}>"


def enviar_email(
    destino: str,
    assunto: str,
    corpo: str,
    anexos: Optional[Iterable[str]] = None,
) -> bool:
    """
    Envia um e-mail de texto simples (com anexos opcionais) para `destino`.

    Retorna True se o envio foi aceito pelo servidor SMTP. Retorna False se o
    e-mail estiver desativado (SMTP não configurado). Levanta EmailError se o
    envio for tentado e falhar — para que a rota chamadora possa avisar o usuário.
    """
    if not settings.EMAIL_HABILITADO:
        logger.warning(
            "Envio de e-mail para %s ignorado: SMTP não configurado no .env "
            "(preencha SMTP_HOST, SMTP_USER e SMTP_PASSWORD).",
            destino,
        )
        return False

    if not destino:
        raise EmailError("Destinatário do e-mail está vazio.")

    msg = EmailMessage()
    msg["From"] = _remetente()
    msg["To"] = destino
    msg["Subject"] = assunto
    msg.set_content(corpo)

    for caminho in anexos or []:
        caminho_abs = os.path.abspath(caminho)
        if not os.path.isfile(caminho_abs):
            logger.error("Anexo não encontrado, será ignorado: %s", caminho_abs)
            continue
        tipo, _ = mimetypes.guess_type(caminho_abs)
        maintype, subtype = (tipo or "application/octet-stream").split("/", 1)
        with open(caminho_abs, "rb") as arquivo:
            msg.add_attachment(
                arquivo.read(),
                maintype=maintype,
                subtype=subtype,
                filename=os.path.basename(caminho_abs),
            )

    try:
        if settings.SMTP_USE_SSL:
            contexto = ssl.create_default_context()
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, context=contexto, timeout=30) as servidor:
                if settings.SMTP_USER:
                    servidor.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                servidor.send_message(msg)
        else:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30) as servidor:
                servidor.ehlo()
                if settings.SMTP_USE_TLS:
                    servidor.starttls(context=ssl.create_default_context())
                    servidor.ehlo()
                if settings.SMTP_USER:
                    servidor.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                servidor.send_message(msg)
    except (smtplib.SMTPException, OSError) as exc:
        logger.error("Falha ao enviar e-mail para %s: %s", destino, exc)
        raise EmailError(str(exc)) from exc

    logger.info("E-mail enviado com sucesso para %s (assunto: %s)", destino, assunto)
    return True
