# Arquitetura do PedroIA

```
┌──────────────────────────────────────────────────────────────┐
│                        VS Code                               │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  Chat (Webview)│  │  Comandos     │  │ Inline Completion │   │
│  │  ChatViewProvider │ /create /fix… │  │ CompletionProvider │   │
│  └───────┬────────┘  └──────┬───────┘  └────────┬─────────┘   │
│          └──────────── PedroIAClient (HTTP) ─────┘            │
└───────────────────────────────┬──────────────────────────────┘
                                 │  REST /api/v1
                                 ▼
┌──────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│                                                              │
│   /chat   /complete   /health   /crm/*                       │
│      │        │                                              │
│      ▼        ▼                                              │
│  ┌─────────────────── ModelRouter ────────────────────┐      │
│  │  auto → cloud (se online) / local (Ollama) / fallback │     │
│  └───────┬───────────────┬───────────────┬────────────┘      │
│          ▼               ▼               ▼                    │
│   Anthropic/OpenAI/   Ollama         Fallback                │
│   Gemini/DeepSeek     (offline)      (config msg)            │
│                                                              │
│   Memory (SQLAlchemy)   Monitoring/Usage   Auth (API key)    │
└───────────────────────────┬──────────────────────────────────┘
                            ▼
              PostgreSQL / SQLite   ·   Redis (opcional)
```

## Componentes

### Extensão (`extension/`, TypeScript)
- **PedroIAClient** — cliente HTTP sem dependências (Node `http`/`https`).
- **ChatViewProvider** — webview do chat com histórico e CSP.
- **CompletionProvider** — `InlineCompletionItemProvider` com debounce e cache.
- **commands/** — comandos slash que montam prompts a partir da seleção.
- **utils/context** — coleta contexto (arquivo, seleção, diagnósticos) automaticamente.

### Backend (`backend/`, Python/FastAPI)
- **llm_engine/router.py** — seleção de provedor e cadeia de fallback.
- **llm_engine/providers/** — um arquivo por provedor, todos implementam `LLMProvider`.
- **llm_engine/prompts.py** — persona de engenheiro sênior + expansão de comandos slash.
- **memory/** — persistência de conversas (base para RAG/embeddings futuros).
- **monitoring/** — logs de uso que alimentam o CRM.
- **auth/** — API key opcional (desativada em modo local).

## Decisão de roteamento

| Modo   | Comportamento                                              |
|--------|-----------------------------------------------------------|
| auto   | online → primeiro cloud disponível; senão Ollama; senão fallback |
| cloud  | primeiro cloud disponível → Ollama → fallback              |
| local  | Ollama → fallback                                          |

Se o provedor selecionado falhar em runtime, o router tenta os demais em cadeia
antes de cair no fallback, garantindo que a extensão sempre receba uma resposta.

## Roadmap técnico
- Streaming de respostas (SSE) no chat e no completion.
- Embeddings + pgvector/LlamaIndex para memória semântica (RAG do projeto).
- Ferramentas de agente (criar/editar arquivos no workspace com confirmação).
- Language Server Protocol para diagnósticos assistidos por IA.
- Empacotamento e publicação no VS Code Marketplace.
