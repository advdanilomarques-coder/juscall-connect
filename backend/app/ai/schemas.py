"""Contratos de dados (schemas) da camada de IA.

Estes tipos padronizam o formato de entrada e saída, INDEPENDENTE do modelo
usado. Assim, quem chama a IA sempre recebe a mesma estrutura, seja a
resposta vinda do Claude, do GPT ou de qualquer outro provedor futuro.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Role(str, Enum):
    """Papéis possíveis numa conversa (padrão de mercado)."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class AIMessage:
    """Uma única mensagem da conversa (entrada padronizada)."""

    role: Role
    content: str


@dataclass
class AIResponse:
    """Resposta padronizada devolvida pela camada de IA (saída padronizada).

    Note que ela carrega metadados (`provider`, `model`, tokens) usados para
    controle de custos e para informar ao administrador qual modelo respondeu.
    """

    content: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    raw: dict = field(default_factory=dict)
