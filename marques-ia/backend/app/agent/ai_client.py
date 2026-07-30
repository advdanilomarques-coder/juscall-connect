# -*- coding: utf-8 -*-
"""
Cliente de IA do Marques IA.

Usa UMA ÚNICA chave de API (OPENROUTER_API_KEY) e tenta, em ordem, os modelos
gratuitos configurados em OPENROUTER_MODEL_PRIMARY / _FALLBACK_1 / _FALLBACK_2.

Se um modelo for removido do tier gratuito, ficar sobrecarregado ou indisponível,
o sistema passa automaticamente para o próximo — sem exigir nenhuma credencial
adicional, já que todos os modelos ':free' são acessados com a mesma chave.
"""
import logging
from typing import List, Optional, Tuple

import httpx

from app.core.config import settings

logger = logging.getLogger("marques_ia.agent")

# Códigos de erro que justificam tentar o próximo modelo da lista.
RETRYABLE_STATUS_CODES = {404, 408, 429, 500, 502, 503}


class AIProviderError(Exception):
    """Levantada quando TODOS os modelos configurados falham."""


async def _call_openrouter(model: str, messages: List[dict]) -> str:
    url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://marquesadvogados.com.br",
        "X-Title": "Marques IA",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 700,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=headers, json=payload)

    if response.status_code in RETRYABLE_STATUS_CODES:
        raise httpx.HTTPStatusError(
            f"Modelo '{model}' retornou HTTP {response.status_code}",
            request=response.request,
            response=response,
        )

    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


async def generate_reply(messages: List[dict]) -> Tuple[str, str]:
    """
    Tenta gerar uma resposta usando os modelos gratuitos configurados, em ordem.

    Retorna (texto_da_resposta, modelo_utilizado).
    Levanta AIProviderError se todos os modelos configurados falharem.
    """
    last_error: Optional[Exception] = None

    for model in settings.OPENROUTER_MODELS_ORDER:
        try:
            logger.info("Tentando modelo de IA: %s", model)
            reply = await _call_openrouter(model, messages)
            return reply, model
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            logger.warning("Falha no modelo '%s': %s", model, exc)
            last_error = exc
            continue

    logger.error("Todos os modelos de IA falharam. Escalando para atendimento humano.")
    raise AIProviderError(str(last_error) if last_error else "Nenhum modelo configurado")
