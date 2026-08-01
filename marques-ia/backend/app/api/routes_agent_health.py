# -*- coding: utf-8 -*-
"""Healthcheck do provedor de IA — usado pelo workflow de monitoramento do n8n."""
from fastapi import APIRouter, Depends

from app.agent.ai_client import AIProviderError, generate_reply
from app.api.deps import require_admin as get_current_admin
from app.models.user import AdminUser

router = APIRouter(prefix="/agent", tags=["agente de ia"])

_MENSAGENS_TESTE = [
    {"role": "system", "content": "Você é um verificador de conectividade."},
    {"role": "user", "content": "Responda apenas 'ok' para confirmar que está funcionando."},
]


@router.get("/healthcheck")
async def healthcheck_ia(_admin: AdminUser = Depends(get_current_admin)):
    """
    Testa se algum dos modelos gratuitos configurados ainda responde.
    Retorna status "ok" com o modelo que respondeu, ou "falha" se todos
    os modelos configurados estiverem indisponíveis (ex.: removidos do
    tier gratuito do OpenRouter) — sinal para trocar o modelo no .env.
    """
    try:
        _texto, modelo = await generate_reply(_MENSAGENS_TESTE)
        return {"status": "ok", "modelo_respondendo": modelo}
    except AIProviderError as exc:
        return {"status": "falha", "detalhe": str(exc)}
