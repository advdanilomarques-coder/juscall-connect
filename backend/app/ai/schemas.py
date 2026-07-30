"""Contratos de dados (schemas) da camada de IA.

Estes tipos padronizam o formato de entrada e saída, INDEPENDENTE do modelo
usado. Assim, quem chama a IA sempre recebe a mesma estrutura, seja a
resposta vinda do Claude, do GPT, do Gemini ou de qualquer provedor futuro.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Role(str, Enum):
    """Papéis possíveis numa conversa (padrão de mercado)."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class TaskType(str, Enum):
    """Tipos de tarefa usados pelo roteamento inteligente de modelos.

    Conforme a seção GERENCIAMENTO INTELIGENTE do documento: cada tipo de
    tarefa pode ser direcionado ao modelo mais adequado (ex.: atendimento →
    Claude, análise jurídica → GPT, resumo → Gemini).
    """

    ATENDIMENTO = "atendimento"
    ANALISE_JURIDICA = "analise_juridica"
    RESUMO = "resumo"
    LEITURA_DOCUMENTO = "leitura_documento"
    CONTRATO = "contrato"


@dataclass
class AIMessage:
    """Uma única mensagem da conversa (entrada padronizada)."""

    role: Role
    content: str


@dataclass
class AIResponse:
    """Resposta padronizada devolvida pela camada de IA (saída padronizada).

    Carrega metadados (`provider`, `model`, tokens, custo, latência) usados
    para controle de custos e para informar ao administrador qual modelo
    respondeu — sem que o cliente final perceba a troca.
    """

    content: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    raw: dict = field(default_factory=dict)
