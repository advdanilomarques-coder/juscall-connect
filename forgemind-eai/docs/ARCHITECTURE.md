# Arquitetura

```
        VS CODE            TERMINAL (CLI)            SITE (web)
           │                    │                       │
      Ghost Text          REPL de chat              Chat / Memória / /config
           └────────────────────┼───────────────────────┘
                                ▼
                    SERVER LOCAL (Fastify @127.0.0.1)
                                │  REST + SSE
                                ▼
                          @forgemind/core
        ┌───────────────┬───────────────┬────────────────┐
        ▼               ▼               ▼                ▼
   Provider Layer   Memory/SQLite   Project Index   Health/Maint.
        │
  ┌─────┼───────────────┐
  ▼     ▼               ▼
Heuristic  LocalLlama   Gemini
(offline)  (offline)    (online, opcional)
```

## Princípios

1. **Offline‑first.** O padrão não usa internet. O provider é uma camada de abstração
   (`AIProvider`) — trocar o cérebro não muda o núcleo (PDF itens 3, 4, 9).
2. **Contexto, não força bruta.** O projeto é indexado incrementalmente (arquivos → símbolos)
   e só o **relevante** é recuperado por consulta. Nunca se envia o projeto inteiro (PDF 16‑18).
3. **Backend fino, núcleo grosso.** VS Code, CLI e site são clientes finos; a inteligência
   vive em `@forgemind/core`. Um só lugar para evoluir.
4. **Segurança por padrão.** Redaction de segredos antes de qualquer log/backup/IA; o servidor
   só escuta em `localhost`; comandos perigosos exigem confirmação (PDF 11, 30, 39).

## Camada de provider

```ts
interface AIProvider {
  name: string;
  offline: boolean;
  health(): Promise<{ ok: boolean; detail: string }>;
  chat(req): AsyncIterable<ChatChunk>;      // streaming
  complete(req): Promise<CompletionResult>; // ghost text, com confidence
}
```

`createProvider(config)` resolve o provider pelo nome configurado. Se o pedido falhar,
o inline cai para o `HeuristicProvider` (que nunca falha e é offline).

## Desvio consciente do PDF

O PDF original especificava backend **Python/FastAPI**. Esta implementação usa
**Node/TypeScript** em todo o monorepo. Motivos (decisão de engenharia, não de moda):

- o ambiente‑alvo é **Node 20/npm 10** → um único toolchain no Mac;
- a inferência local offline (`node-llama-cpp`) é **nativa de Node**;
- a extensão VS Code já é TypeScript.

A arquitetura de provider/índice/memória é idêntica à do PDF; só a linguagem do backend mudou.
