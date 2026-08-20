# Instalação

## Requisitos

- **Node.js 20.x** e **npm 10.x** (o `install.sh` valida).
- macOS Intel (x86_64) é o alvo prioritário, mas roda em qualquer SO com Node 20+.
- Internet **uma vez** (para `npm install` e, opcionalmente, baixar o modelo). Depois, offline.

## Passos

```bash
cd forgemind-eai
./scripts/install.sh
```

Isso: valida o ambiente, cria `.env` a partir de `.env.example`, roda `npm install`,
compila `core`/`server`/`cli` e o site.

## Rodar

```bash
# terminal (chat estilo Claude Code)
node packages/cli/dist/index.js

# site local
./scripts/start.sh          # http://127.0.0.1:4319
```

Dica: crie um atalho no shell:
```bash
alias forgemind="node $(pwd)/packages/cli/dist/index.js"
```

## Cérebro local (opcional, conversa natural offline)

```bash
./scripts/model-pull.sh 3b
npm install node-llama-cpp --workspace @forgemind/core
# escolha "local-llama" em /config
```

## Extensão VS Code

```bash
npm run build:extension
# para instalar como .vsix:
npm i -g @vscode/vsce
cd packages/extension && vsce package
# depois: VS Code > Extensions > "..." > Install from VSIX
```

A extensão fala com o backend local (`http://127.0.0.1:4319`). Suba o servidor antes.

## Serviço persistente (macOS)

```bash
./scripts/service-macos.sh install     # inicia no login (LaunchAgent)
./scripts/service-macos.sh uninstall
```

## Manutenção

```bash
./scripts/maintenance.sh --diagnose
./scripts/maintenance.sh --repair      # reparos seguros; nunca apaga dados
./scripts/backup.sh                    # exporta memória/histórico (sem segredos)
```
