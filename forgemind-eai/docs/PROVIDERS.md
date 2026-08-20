# Providers

O ForgeMind separa **interface** de **cérebro**. Você escolhe o cérebro em `/config` (site)
ou via `.env` (`AI_PROVIDER=...`).

## heuristic (padrão, offline)

Motor determinístico, sem modelo e sem download. Forte em:
- Ghost Text por análise sintática (pares, indentação, padrões de linguagem, símbolos do projeto);
- sugestões de terminal por histórico/heurística;
- respostas de ajuda baseadas em regras.

Não é um LLM — não "conversa" sobre assuntos gerais em profundidade. Use‑o como turbo instantâneo.

## local-llama (offline, recomendado para conversa)

LLM local via [`node-llama-cpp`](https://github.com/withcatai/node-llama-cpp) (llama.cpp).
**Não é Ollama e não hospeda nada.** Roda um GGUF direto na CPU.

```bash
./scripts/model-pull.sh 3b      # Qwen2.5-3B (~2GB) — recomendado p/ 10GB RAM
./scripts/model-pull.sh 1.5b    # modo rápido (menos RAM)
npm install node-llama-cpp --workspace @forgemind/core
```

Depois: em `/config` escolha `local-llama` e confirme o caminho do modelo.

**Expectativa de desempenho em Mac Intel antigo (DDR3):** respostas em segundos a dezenas de
segundos, dependendo do tamanho do modelo. É o preço do offline ilimitado e gratuito.

### Escolha de modelo

| Modelo | RAM | Velocidade (Intel antigo) | Qualidade geral |
|---|---|---|---|
| Qwen2.5‑1.5B | ~1.5 GB | mais rápida | básica |
| **Qwen2.5‑3B** | ~3 GB | média | **boa (recomendado)** |
| Qwen2.5‑7B | ~6 GB | lenta | melhor (Mac 16GB+) |

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
