<div align="center">

<img src="media/icon.png" width="120" alt="PedroIA" />

# PedroIA

### Seu engenheiro de inteligência artificial dentro do VS Code

Chat, autocomplete e comandos que entendem o seu projeto — cria, corrige, explica e refatora código.

</div>

---

> **Adicione aqui um GIF/print da extensão em ação** (`media/demo.gif`).
> Ex.: o chat respondendo, o autocomplete sugerindo, o menu de contexto.
> Extensões com uma boa demonstração recebem muito mais instalações.

## ✨ O que o PedroIA faz

- **💬 Chat integrado** — converse com um engenheiro sênior sem sair do editor, com histórico e memória.
- **⚡ Autocomplete inline** — sugestões enquanto você digita, no estilo Copilot.
- **🛠️ Comandos** — `/create`, `/explain`, `/fix`, `/refactor`, `/test`, `/security` na paleta e no menu de contexto.
- **🧠 Contexto automático** — lê o arquivo ativo, a seleção e os erros. Sem prompts gigantes.
- **🔌 Vários modelos** — Claude, OpenAI, Gemini, DeepSeek e modelos locais (Ollama).

## 🚀 Começando

1. Instale a extensão.
2. Abra as **Configurações** → procure por **PedroIA**.
3. Preencha:
   - `pedroia.backendUrl` — o endereço do serviço PedroIA.
   - `pedroia.apiKey` — a sua chave de acesso (se o serviço exigir).
4. Clique no ícone do **PedroIA** na barra lateral e comece a conversar.

Atalho do chat: **Ctrl+Shift+I** (Mac: **Cmd+Shift+I**).

## ⚙️ Configurações

| Configuração                    | Padrão                     | Descrição                              |
|---------------------------------|----------------------------|----------------------------------------|
| `pedroia.backendUrl`            | `http://127.0.0.1:8000`    | Endereço do serviço PedroIA            |
| `pedroia.apiKey`                | vazio                      | Chave de acesso ao serviço             |
| `pedroia.preferredMode`         | `auto`                     | `auto` / `cloud` / `local`             |
| `pedroia.completion.enabled`    | `true`                     | Liga/desliga o autocomplete            |
| `pedroia.completion.debounceMs` | `350`                      | Atraso antes de sugerir                |

## 🧩 Comandos

| Comando            | O que faz                          |
|--------------------|------------------------------------|
| `PedroIA: Abrir Chat`         | Abre o chat na barra lateral  |
| `/create`          | Cria projeto ou código             |
| `/explain`         | Explica o código selecionado       |
| `/fix`             | Corrige erros                      |
| `/refactor`        | Melhora o código                   |
| `/test`            | Cria testes automatizados          |
| `/security`        | Analisa vulnerabilidades           |

## 🔒 Privacidade

O código enviado para análise é processado pelo serviço PedroIA configurado em `backendUrl`
e pelo provedor de IA escolhido. Use um serviço de sua confiança e não envie segredos.

## 📄 Licença

[MIT](../LICENSE) · Feito para desenvolvedores.
