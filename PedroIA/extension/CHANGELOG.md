# Changelog

Todas as mudanças relevantes desta extensão são documentadas aqui.
O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

## [0.3.0] — 2026-08-09

### Adicionado
- **Chat em tela cheia**: botão no topo do painel e comando "Abrir Chat em Tela Cheia".
- Conhecimentos gerais (não só código) na descrição e no comportamento.

### Alterado
- **Autocomplete recalibrado** (estilo Copilot): mais calmo, contexto-aware, 1 linha por
  padrão e multilinha só quando o bloco abre; saída limpa (sem crases/eco/lixo).
- Suporte a **muitos caracteres** (limites ampliados) com aviso claro quando excede.

### Corrigido
- **Ajuda no terminal** agora funciona: lê a seleção com timing correto e, se não houver
  seleção, pede o texto por um campo.
- Mensagens e status renomeados de "PedroIA" para "Clean Code".

## [0.2.0] — 2026-08-08

### Adicionado
- **Renomeada para "Clean Code"** (marca, comandos e configurações `cleancode.*`).
- **Perguntar sobre a seleção** (`Cmd/Ctrl+L`): abre o chat com o código já anexado (estilo Blackbox).
- **Ajuda no terminal** (`Cmd/Ctrl+Alt+T` ou menu de contexto do terminal): lê a seleção e sugere o comando certo.
- Novos comandos: `/document`, `/comment`, `/optimize`, `/review`, `/convert`, `/terminal`, `/commit`.
- Banner e README profissional para o Marketplace.

### Alterado
- Respostas mais curtas, naturais e com emojis.
- `backendUrl` já vem apontando para o servidor hospedado por padrão.

## [0.1.0] — 2026-08-02

### Adicionado
- Chat integrado na barra lateral, com histórico e seletor de modo (Auto / Cloud / Local).
- Autocomplete inline (PedroIA Code Completion Engine) com debounce e cache.
- Comandos: `/create`, `/explain`, `/fix`, `/refactor`, `/test`, `/security`.
- Coleta automática de contexto (arquivo ativo, seleção, diagnósticos, workspace).
- Integração com backend multi-LLM (Claude, OpenAI, Gemini, DeepSeek, Ollama).
- Ícone, item na barra de status e menu de contexto do editor.
