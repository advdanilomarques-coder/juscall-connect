# PedroIA — Seu engenheiro de IA no VS Code

**Uma IA profissional integrada ao VS Code capaz de criar, corrigir e evoluir seus projetos.**

O PedroIA traz para o seu editor:

- 💬 **Chat inteligente** — pergunte sobre o seu código, peça soluções, tire dúvidas.
- 🧠 **Explicar seleção** — selecione um trecho, clique com o botão direito → *PedroIA: Explicar seleção*.
- ⚡ **Autocomplete estilo Copilot** — sugestões inline enquanto você digita, em qualquer linguagem.

## Como usar

1. Abra a paleta de comandos (`Ctrl+Shift+P`) e rode **PedroIA: Perguntar / Abrir chat** — ou use o atalho `Ctrl+Alt+P` (`Cmd+Alt+P` no Mac).
2. Configure em **Settings → PedroIA**:
   - `pedroia.backendUrl` — a URL do seu backend (ex.: `https://pedroia-backend.onrender.com`).
   - `pedroia.apiKey` — a sua chave de acesso (uma das `API_KEYS` do backend).
3. Comece a conversar. Para autocomplete, é só digitar — as sugestões aparecem inline (aceite com `Tab`).

## Configurações

| Configuração | Padrão | Descrição |
|---|---|---|
| `pedroia.backendUrl` | `https://pedroia-backend.onrender.com` | URL do backend do PedroIA. |
| `pedroia.apiKey` | `""` | Chave de acesso da extensão. |
| `pedroia.enableAutocomplete` | `true` | Liga/desliga o autocomplete inline. |
| `pedroia.autocompleteDebounceMs` | `400` | Espera antes de pedir sugestão. |

## Privacidade

A extensão nunca guarda a chave da Anthropic — ela fica apenas no backend. O código que você envia é usado só para gerar a resposta.

---

Feito com ❤️ e Claude.
