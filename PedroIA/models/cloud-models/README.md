# Modelos em nuvem

Quando há internet e uma chave configurada, o PedroIA usa provedores de nuvem.
A ordem de prioridade padrão é: **anthropic → openai → gemini → deepseek**
(configurável em `Settings.cloud_priority`).

| Provedor  | Variável de ambiente   | Modelo padrão                  |
|-----------|------------------------|--------------------------------|
| Anthropic | `ANTHROPIC_API_KEY`    | `claude-3-5-sonnet-latest`     |
| OpenAI    | `OPENAI_API_KEY`       | `gpt-4o-mini`                  |
| Gemini    | `GEMINI_API_KEY`       | `gemini-1.5-flash`             |
| DeepSeek  | `DEEPSEEK_API_KEY`     | `deepseek-chat`                |

Basta definir **pelo menos uma** chave em `backend/.env`. Provedores sem chave são
ignorados automaticamente. Se nenhuma chave existir e o Ollama não estiver rodando,
o backend responde em "modo de configuração" com instruções.
