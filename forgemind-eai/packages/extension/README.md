# ForgeMind EAI — Extensão VS Code

Ghost Text (inline), chat e Terminal AI ligados ao backend local do ForgeMind.
Toda a inteligência roda localmente (offline); a extensão é fina e só orquestra.

## Requisitos
- Backend ForgeMind rodando: `./scripts/start.sh` (padrão `http://127.0.0.1:4319`).

## Recursos
- **Inline / Ghost Text** contextual (usa o índice do projeto).
- **ForgeMind: Abrir Chat** — chat lateral.
- **ForgeMind: Explicar seleção** — explica o código selecionado.
- **ForgeMind: Indexar projeto** — atualiza o índice para o contexto cruzado.
- **ForgeMind: Abrir meu site (localhost)**.

## Configuração
- `forgemind.serverUrl` — URL do backend (padrão `http://127.0.0.1:4319`).
- `forgemind.inlineEnabled` — liga/desliga o Ghost Text.
