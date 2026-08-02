# PedroIA — Extensão VS Code

Seu engenheiro de inteligência artificial dentro do VS Code: chat, autocomplete inline
e comandos para criar, corrigir, explicar e refatorar código.

## Recursos

- **Chat lateral** (Ctrl/Cmd+Shift+I) com histórico e seleção de modo (Auto / Cloud / Local).
- **Autocomplete inline** (PedroIA Code Completion Engine) — sugestões estilo Copilot.
- **Comandos** no menu de contexto e na paleta:
  - `/create` — criar projeto/código
  - `/explain` — explicar código
  - `/fix` — corrigir erros
  - `/refactor` — melhorar código
  - `/test` — criar testes
  - `/security` — analisar segurança
- **Contexto automático**: lê o arquivo ativo, a seleção, os diagnósticos e o workspace —
  você não precisa colar prompts gigantes.

## Como funciona

A extensão é um cliente fino que fala com o **backend PedroIA** (FastAPI). O backend decide
qual modelo usar (nuvem quando há internet, Ollama local quando offline).

## Desenvolvimento

```bash
npm install
npm run esbuild      # ou: npm run watch
# Pressione F5 no VS Code para abrir uma janela de desenvolvimento
```

Configure em **Settings → PedroIA**:

- `pedroia.backendUrl` (padrão `http://127.0.0.1:8000`)
- `pedroia.apiKey` (opcional em modo local)
- `pedroia.preferredMode` (`auto` / `cloud` / `local`)
- `pedroia.completion.enabled`

## Empacotar (.vsix)

```bash
npm install -g @vscode/vsce
vsce package
```

> Observação: para publicar, adicione um `media/icon.png` (128×128). O ícone da barra lateral
> já é fornecido como SVG.
