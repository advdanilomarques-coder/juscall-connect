# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    telefone: str = Field(
        ...,
        description="Telefone do cliente (mesmo identificador usado no WhatsApp), ex: 5511991537423",
    )
    mensagem: str = Field(..., description="Mensagem enviada pelo cliente")
    nome_cliente: Optional[str] = Field(
        None, description="Nome do cliente, se informado nesta mensagem"
    )


class ChatResponse(BaseModel):
    texto: str
    modelo_utilizado: Optional[str]
    escalado_para_humano: bool
    cliente_novo: bool
