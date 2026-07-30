# -*- coding: utf-8 -*-
"""
Valida se a OPENROUTER_API_KEY configurada consegue chamar ao menos um dos
modelos gratuitos definidos no .env. Usado pelo install-all.sh antes de subir
a aplicação, para detectar cedo se um modelo ':free' saiu do ar.
"""
import asyncio
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.agent.ai_client import AIProviderError, generate_reply  # noqa: E402
from app.core.config import settings                              # noqa: E402


async def main() -> None:
    mensagens = [
        {"role": "system", "content": "Você é um verificador de conectividade."},
        {"role": "user", "content": "Responda apenas 'ok' para confirmar que está funcionando."},
    ]

    print(f"Testando modelos configurados (em ordem): {settings.OPENROUTER_MODELS_ORDER}")

    try:
        texto, modelo = await generate_reply(mensagens)
        print(f"Sucesso. Modelo respondendo: {modelo}")
        print(f"Resposta de teste: {texto[:80]!r}")
    except AIProviderError as exc:
        print("ERRO: nenhum dos modelos gratuitos configurados respondeu.")
        print(f"Detalhe: {exc}")
        print("Verifique OPENROUTER_API_KEY e os nomes dos modelos no .env "
              "(modelos ':free' podem ser removidos do OpenRouter sem aviso).")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
