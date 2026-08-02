# Modelos locais (offline)

O PedroIA usa o **Ollama** para rodar modelos localmente quando não há internet
(ou quando `pedroia.preferredMode = local`).

## Instalação

```bash
# https://ollama.com/download
curl -fsSL https://ollama.com/install.sh | sh
```

## Modelos recomendados

| Uso            | Modelo                    | Comando                                  |
|----------------|---------------------------|------------------------------------------|
| Chat geral     | Llama 3.1 8B              | `ollama pull llama3.1`                    |
| Chat leve      | Mistral 7B                | `ollama pull mistral`                     |
| Autocomplete   | Qwen2.5-Coder 1.5B (FIM)  | `ollama pull qwen2.5-coder:1.5b`          |
| Código maior   | Qwen2.5-Coder 7B          | `ollama pull qwen2.5-coder:7b`            |

Configure os nomes em `backend/.env`:

```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
OLLAMA_COMPLETION_MODEL=qwen2.5-coder:1.5b
```

> O modelo de autocomplete usa *fill-in-the-middle* (parâmetro `suffix` da API do Ollama),
> por isso um modelo "coder" com suporte a FIM é recomendado.
