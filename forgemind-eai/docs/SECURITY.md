# Segurança & Privacidade

O ForgeMind foi desenhado como sistema **local‑first**. Modelo de ameaça e controles:

## Superfície de ataque

- **Servidor HTTP local.** Escuta **apenas** em `127.0.0.1` (não `0.0.0.0`). CORS restrito a
  origens `localhost`/`127.0.0.1`. Não há autenticação porque não há exposição de rede — se você
  mudar o host para um IP público, **adicione autenticação primeiro** (não suportado por padrão).
- **Sem hospedagem.** Nada é publicado. O "site" é servido pelo seu próprio backend.

## Segredos (PDF 11, 47)

- API keys vêm **só do ambiente** (`GEMINI_API_KEY`). Nunca são gravadas em `config.json`.
- `redactSecrets()` roda antes de **todo** log, backup e resposta de API. Redige chaves Google/OpenAI/GitHub,
  JWTs, headers Authorization e blocos PEM.
- O indexador **ignora** arquivos sensíveis (`.env`, `.pem`, `.key`, `id_rsa`, `.p12`…) — eles
  nunca entram no índice, na memória, em logs ou em backups.

## Dados

- Tudo em `~/.forgemind` (SQLite + logs + backups), na sua máquina.
- Memória é **apagável e exportável** (`/api/memory`, `forgemind backup`).
- `reset` (quando usado) exige confirmação explícita antes de apagar.

## Providers externos

- Só o provider `gemini` envia conteúdo para fora. Ele é **opcional e desligado por padrão**.
- Ao usá‑lo, lembre‑se: o que você mandar pode sair da máquina. O ForgeMind avisa o modo ("online").

## Terminal (PDF 30)

- O Terminal AI **sugere e explica**, mas **nunca executa** automaticamente.
- Comandos perigosos (`rm -rf`, `git push --force`, `chmod -R 777`, `dd`, `mkfs`…) são marcados
  e exigem confirmação.

## Recomendações

- Rode `./scripts/backup.sh` periodicamente.
- Não altere `FORGEMIND_HOST` para expor na rede sem colocar um proxy autenticado à frente.
- Mantenha o `.env` fora do controle de versão (já está no `.gitignore`).
