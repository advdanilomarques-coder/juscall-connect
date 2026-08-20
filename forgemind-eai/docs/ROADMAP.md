# Roadmap

Estado atual: **fundação funcional (v0.1)**. O que já roda e o que vem a seguir.

## v0.1 — feito

- [x] Monorepo TypeScript (core, server, cli, web, extension).
- [x] Camada de provider plugável: `heuristic` (offline), `local-llama` (offline), `gemini` (online).
- [x] SQLite local com migrations, memória, histórico, FTS (pesquisa).
- [x] Índice de projeto incremental (arquivos + símbolos, agnóstico à linguagem).
- [x] Context retriever (recupera só o relevante).
- [x] Ghost Text heurístico (editor e terminal) com confidence gate.
- [x] Terminal AI: explicar/sugerir comandos, marcação de perigosos.
- [x] CLI com REPL de chat estilo Claude Code + comando `localhost`.
- [x] Site próprio (chat streaming, memória, `/config`, tema claro/escuro).
- [x] Extensão VS Code (inline completion, chat, explicar seleção).
- [x] Health monitor + scripts de manutenção/backup + LaunchAgent.
- [x] Redaction de segredos + testes (vitest).

## v0.2 — próximos passos sugeridos

- [ ] Inline com LLM local para blocos maiores (hoje o inline é heurístico mesmo com modelo).
- [ ] Índice semântico (embeddings locais) para recuperação por significado, não só por nome.
- [ ] Métricas do inline (aceitação, latência, cache hit) na UI.
- [ ] Auto‑maintenance ativa (watchdog que reinicia processos caídos).
- [ ] Histórico de conversas navegável no site (sidebar com conversas salvas).
- [ ] Empacotamento `.vsix` publicável e `.app`/serviço com uninstaller.
- [ ] Modo híbrido automático (roteamento local→gemini por dificuldade da pergunta).

## Ideias futuras

- Multi‑agente (planner/executor/reviewer) para tarefas de código maiores.
- RAG sobre a documentação do próprio projeto.
- Suporte a mais runtimes de modelo local (MLX quando em Apple Silicon).
