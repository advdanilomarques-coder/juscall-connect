# ForgeMind EAI

**IA pessoal de desenvolvimento e conhecimento geral — local, offline e sem hospedagem.**

Terminal + site próprio + extensão VS Code. Sem Ollama. Roda no seu Mac Intel.

---

## O que é

O ForgeMind é uma IA de desenvolvimento que **compreende antes de sugerir**. Ela roda
inteiramente na sua máquina: chat, memória, histórico, índice de projeto, Ghost Text,
Terminal AI, health monitor e auto‑manutenção. Nada é hospedado; nada sai do seu computador
(exceto se você, opcionalmente, ativar um provider online).

> **Modo de operação:** por padrão o ForgeMind **não executa modelos pesados** nem depende de
> internet. O "cérebro" é escolhido por configuração (ver **Providers**). O padrão é offline.

## Providers (o "cérebro") — arquitetura plugável

| Provider | Internet | Modelo | Quando usar |
|---|---|---|---|
| `heuristic` *(padrão)* | ❌ não | nenhum | Instantâneo. Completar código, comandos e ajuda. Sempre funciona. |
| `local-llama` | ❌ não* | GGUF local (ex.: Qwen2.5‑3B) | Conversa natural + assuntos gerais, offline e ilimitado. |
| `gemini` | ✅ sim | Google Gemini | Qualidade máxima sob demanda. Opcional, desligado por padrão. |

*\*`local-llama` precisa de internet **uma vez** para baixar o modelo; depois é 100% offline.*

Recomendado para Mac Intel com ~10 GB de RAM: **`local-llama` com Qwen2.5‑3B (Q4)**.
Não usa Ollama — usa `node-llama-cpp` (llama.cpp nativo em Node).

## Instalação rápida

```bash
cd forgemind-eai
./scripts/install.sh          # valida Node 20+, instala deps e compila
```

## Uso

**Terminal (estilo Claude Code):**
```bash
node packages/cli/dist/index.js        # abre o chat no terminal
# dentro do chat: /help, /site, /health, /index, /memory
```

**Seu site local:**
```bash
./scripts/start.sh            # sobe em http://127.0.0.1:4319
# ou, no chat/CLI, digite: localhost   -> ele te devolve a URL do seu site
```

**Ativar o cérebro local (conversa natural offline):**
```bash
./scripts/model-pull.sh                # baixa Qwen2.5-3B (uma vez)
npm install node-llama-cpp --workspace @forgemind/core
# em /config do site, escolha o provider "local-llama"
```

**Extensão VS Code:**
```bash
npm run build:extension
# em models/ pesados ou grandes builds: veja docs/INSTALL.md para empacotar (.vsix)
```

## Comando `localhost`

Sempre que você digitar **`localhost`** (no terminal do ForgeMind ou no chat do site),
ele responde com a URL do **seu** site local para você conversar por lá também.
Também disponível como `forgemind localhost` e no comando "ForgeMind: Abrir meu site" do VS Code.

## Estrutura

```
forgemind-eai/
├── packages/
│   ├── core/        # providers, SQLite, memória, índice, contexto, ghost text, health
│   ├── server/      # backend local (Fastify) — serve o site + API. Só localhost.
│   ├── cli/         # CLI + REPL de chat estilo Claude Code
│   ├── web/         # seu site (React + Vite): chat, memória, /config
│   └── extension/   # extensão VS Code: Ghost Text + chat + Terminal AI
├── scripts/         # install, start, stop, doctor, maintenance, backup, model-pull, service
└── docs/            # arquitetura, instalação, providers, segurança, roadmap
```

## Privacidade

- Dados (conversas, memória, índice) ficam em `~/.forgemind` — **na sua máquina**.
- Segredos (`.env`, API keys, `.pem`) **nunca** são indexados, logados ou incluídos em backups (redaction ativa).
- O site escuta **apenas** em `127.0.0.1`. Nada é publicado na internet.

## Documentação

- [Arquitetura](docs/ARCHITECTURE.md) · [Instalação](docs/INSTALL.md) · [Providers](docs/PROVIDERS.md) · [Segurança](docs/SECURITY.md) · [Roadmap](docs/ROADMAP.md)

## Licença

MIT — uso pessoal.
