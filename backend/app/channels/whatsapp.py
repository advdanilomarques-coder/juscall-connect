"""Integração com a WhatsApp Business API (Meta Cloud API).

Responsabilidades:
  * Verificar o webhook (handshake exigido pela Meta na configuração).
  * Interpretar o payload de mensagens recebidas → IncomingMessage.
  * Enviar mensagens de texto de volta ao cliente.

Documentação: https://developers.facebook.com/docs/whatsapp/cloud-api

Requer no .env: WHATSAPP_ACCESS_TOKEN, WHATSAPP_PHONE_NUMBER_ID e
WHATSAPP_VERIFY_TOKEN. Sem eles, o cliente fica "não configurado" e apenas
loga a resposta (útil para desenvolvimento sem conta da Meta).
"""

from __future__ import annotations

from app.channels.base import ChannelClient, IncomingMessage
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class WhatsAppClient(ChannelClient):
    """Cliente da WhatsApp Cloud API."""

    name = "whatsapp"

    def __init__(self) -> None:
        self._token = settings.whatsapp_token
        self._phone_id = settings.whatsapp_phone_number_id
        self._app_secret = settings.whatsapp_app_secret
        self._base = settings.whatsapp_api_base.rstrip("/")

    @property
    def configured(self) -> bool:
        return bool(self._token and self._phone_id)

    def verify_signature(self, body: bytes, signature_header: str | None) -> bool:
        """Valida a assinatura X-Hub-Signature-256 enviada pela Meta.

        A Meta assina cada webhook com HMAC-SHA256 usando o APP_SECRET. Isso
        garante que a requisição realmente veio da Meta (e não de um impostor).
        Se o APP_SECRET não estiver configurado, a validação é ignorada (modo
        desenvolvimento) — configure-o em produção.
        """
        if not self._app_secret:
            return True  # sem segredo configurado: não valida (dev)
        if not signature_header or not signature_header.startswith("sha256="):
            return False
        import hashlib
        import hmac

        expected = hmac.new(
            self._app_secret.encode("utf-8"), body, hashlib.sha256
        ).hexdigest()
        received = signature_header.split("=", 1)[1]
        return hmac.compare_digest(expected, received)

    def verify(self, mode: str | None, token: str | None, challenge: str | None) -> str | None:
        """Valida o handshake do webhook. Retorna o challenge se OK, senão None.

        A Meta chama GET com hub.mode=subscribe e hub.verify_token; devemos
        devolver o hub.challenge se o token bater com o configurado.
        """
        if mode == "subscribe" and token and token == settings.whatsapp_verify_token:
            return challenge
        return None

    def parse_webhook(self, payload: dict) -> list[IncomingMessage]:
        """Extrai as mensagens de texto de um payload de webhook da Meta.

        O payload é aninhado (entry → changes → value → messages). Ignoramos
        eventos que não sejam mensagens de texto (status, mídia sem texto...).
        """
        messages: list[IncomingMessage] = []
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                contacts = value.get("contacts", [])
                # Mapeia wa_id -> nome do contato (quando disponível).
                names = {
                    c.get("wa_id"): c.get("profile", {}).get("name")
                    for c in contacts
                }
                for msg in value.get("messages", []):
                    if msg.get("type") != "text":
                        continue
                    sender = msg.get("from", "")
                    text = msg.get("text", {}).get("body", "")
                    if sender and text:
                        messages.append(
                            IncomingMessage(
                                channel=self.name,
                                sender=sender,
                                text=text,
                                name=names.get(sender),
                            )
                        )
        return messages

    async def send_text(self, to: str, text: str) -> None:
        """Envia uma mensagem de texto ao cliente via Cloud API."""
        if not text:
            return
        if not self.configured:
            # Modo desenvolvimento: sem credenciais, apenas registramos.
            logger.info("[WhatsApp NÃO configurado] Para %s: %s", to, text)
            return

        try:
            import httpx
        except ImportError:
            logger.error("httpx não instalado — impossível enviar ao WhatsApp.")
            return

        url = f"{self._base}/{self._phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text},
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
        except Exception as exc:
            logger.error("Falha ao enviar mensagem ao WhatsApp: %s", exc)


# Instância única compartilhada.
whatsapp_client = WhatsAppClient()
