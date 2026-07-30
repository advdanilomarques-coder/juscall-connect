"""Estimativa de custo por provedor/modelo (CONTROLE DE CUSTOS).

O documento exige registrar o valor estimado de cada requisição. Aqui
mantemos uma tabela simples de preços por 1 milhão de tokens (USD), separada
para entrada (input) e saída (output).

IMPORTANTE: preços de IA mudam com frequência. Esta tabela é uma ESTIMATIVA
para o painel administrativo — ajuste conforme os valores oficiais de cada
provedor. Modelos não listados assumem custo 0 (ex.: Ollama local é gratuito).
"""

from __future__ import annotations

# Preço em USD por 1.000.000 de tokens: (input, output).
_PRICE_PER_MTOK: dict[str, tuple[float, float]] = {
    # Claude (Anthropic)
    "claude-opus-4-8": (15.0, 75.0),
    "claude-3-5-sonnet": (3.0, 15.0),
    "claude-3-5-haiku": (0.8, 4.0),
    # OpenAI
    "gpt-4o": (2.5, 10.0),
    "gpt-4o-mini": (0.15, 0.6),
    # Gemini (camada gratuita não gera custo; valores da camada paga)
    "gemini-2.0-flash": (0.1, 0.4),
    "gemini-1.5-pro": (1.25, 5.0),
    # DeepSeek
    "deepseek-chat": (0.27, 1.1),
    # Mistral
    "mistral-large-latest": (2.0, 6.0),
    # Grok (xAI)
    "grok-2-latest": (2.0, 10.0),
}


def _match_price(model: str) -> tuple[float, float]:
    """Encontra o preço pelo prefixo do nome do modelo (tolerante a sufixos)."""
    model = (model or "").lower()
    for key, price in _PRICE_PER_MTOK.items():
        if model.startswith(key) or key in model:
            return price
    return (0.0, 0.0)


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calcula o custo estimado (USD) de uma requisição.

    Fórmula: (tokens / 1_000_000) * preço_por_milhão, somando entrada e saída.
    """
    in_price, out_price = _match_price(model)
    cost = (input_tokens / 1_000_000) * in_price
    cost += (output_tokens / 1_000_000) * out_price
    return round(cost, 6)
