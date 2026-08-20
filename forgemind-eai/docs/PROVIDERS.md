# Providers

O ForgeMind separa **interface** de **cérebro**. Você escolhe o cérebro em `/config` (site)
ou via `.env` (`AI_PROVIDER=...`).

## heuristic (padrão, offline)

Motor determinístico, sem modelo e sem download. Forte em:
- Ghost Text por análise sintática (pares, indentação, padrões de linguagem, símbolos do projeto);
- sugestões de terminal por histórico/heurística;
- respostas de ajuda baseadas em regras.

Não é um LLM — não "conversa" sobre assuntos gerais em profundidade. Use‑o como turbo instantâneo.

## local-llama (offline, recomendado para código e inline)

LLM local via [`node-llama-cpp`](https://github.com/withcatai/node-llama-cpp) (llama.cpp).
**Não é Ollama e não hospeda nada.** Roda um GGUF direto na CPU.

```bash
./scripts/model-pull.sh 3b      # Qwen2.5-Coder-3B (~2GB) — código + FIM p/ inline
./scripts/model-pull.sh 1.5b    # modo rápido (menos RAM)
npm install node-llama-cpp --workspace @forgemind/core
```

Depois: em `/config` escolha `local-llama` e confirme o caminho do modelo.

**Por que Qwen2.5‑Coder:** é forte em código e **suporta FIM/infill**, que é o que o Ghost Text
usa para completar no meio do arquivo (prefixo + sufixo). Também responde assuntos gerais.

**Inline (Ghost Text) com modelo:** o `complete()` usa `generateInfillCompletion(prefix, suffix)`
com orçamento curto por nível (LOW/BALANCED/HIGH), **timeout** e **cache**; se o modelo demorar
ou não estiver pronto, cai no motor heurístico — o editor nunca trava (PDF 24/25/31).

**Expectativa de desempenho em Mac Intel antigo (DDR3):** respostas de chat em segundos a
dezenas de segundos; inline curto é mais rápido. É o preço do offline ilimitado e gratuito.

### Escolha de modelo

| Modelo | RAM | Velocidade (Intel antigo) | Uso |
|---|---|---|---|
| Qwen2.5‑Coder‑1.5B | ~1.5 GB | mais rápida | inline leve / modo rápido |
| **Qwen2.5‑Coder‑3B** | ~3 GB | média | **código + inline (recomendado)** |
| Qwen2.5‑Coder‑7B | ~6 GB | lenta | melhor qualidade (Mac 16GB+) |

## gemini (online, opcional)

Provider externo (Google Gemini). Desligado por padrão. A chamada ocorre **no backend**;
a API key vem só do ambiente (`GEMINI_API_KEY`) e **nunca** é gravada em disco nem exposta ao site.

```bash
# .env
AI_PROVIDER=gemini
GEMINI_API_KEY=sua-chave
GEMINI_MODEL=gemini-1.5-flash
```

## Modo híbrido

Deixe `local-llama` como padrão (offline, ilimitado) e troque pontualmente para `gemini`
quando quiser qualidade máxima e estiver online. A troca é imediata em `/config`.
