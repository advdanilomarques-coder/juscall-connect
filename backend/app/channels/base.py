"""Contrato dos canais de atendimento.

Define a interface mínima que todo canal deve oferecer para enviar uma
mensagem de volta ao cliente. A recepção (webhook) é específica de cada
canal, mas o ENVIO é padronizado por esta interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class IncomingMessage:
    """Mensagem recebida, já normalizada, independente do canal de origem."""

    channel: str          # "whatsapp", "telegram", ...
    sender: str           # identificador do cliente (telefone, chat_id...)
    text: str             # conteúdo textual da mensagem
    name: str | None = None   # nome do contato, quando o canal informa


class ChannelClient(ABC):
    """Interface para enviar mensagens em um canal específico."""

    name: str = "base"

    @abstractmethod
    async def send_text(self, to: str, text: str) -> None:
        """Envia uma mensagem de texto ao destinatário `to`."""
        raise NotImplementedError
