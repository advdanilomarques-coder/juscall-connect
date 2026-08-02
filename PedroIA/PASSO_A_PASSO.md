# 🚀 PedroIA — Passo a passo (comece aqui)

Este guia leva você do zero até o PedroIA rodando no VS Code. Siga na ordem.

> **Tempo estimado:** 10–15 minutos.
> **Já está tudo pronto no repositório** — você não precisa criar nenhum arquivo. Só executar os comandos abaixo.

---

## ✅ 0. Pré-requisitos

Instale (se ainda não tiver):

| Ferramenta | Versão | Como verificar        | Onde baixar                         |
|------------|--------|-----------------------|-------------------------------------|
| Python     | 3.11+  | `python3 --version`   | https://www.python.org/downloads    |
| Node.js    | 18+    | `node --version`      | https://nodejs.org                  |
| npm        | 9+     | `npm --version`       | (vem com o Node)                    |
| Git        | any    | `git --version`       | https://git-scm.com                 |
| VS Code    | 1.85+  | abrir o programa      | https://code.visualstudio.com       |

**Opcional (modo offline):** Ollama — https://ollama.com/download

---

## 📥 1. Baixar o código

O PedroIA está na branch `claude/pedroia-vscode-extension-tq50xm` do seu repositório.

```bash
# entre na pasta do seu repositório (a que você já clonou)
cd caminho/para/juscall-connect

# baixe e entre na branch com o PedroIA
git fetch origin
git checkout claude/pedroia-vscode-extension-tq50xm
git pull origin claude/pedroia-vscode-extension-tq50xm

# entre na pasta do projeto
cd PedroIA
```

Confira se você está no lugar certo:

```bash
ls
# deve mostrar: backend  extension  frontend  crm  docker  install.sh  README.md ...
```

---

## ⚙️ 2. Instalação automática

```bash
bash install.sh
```

Isso faz **tudo** automaticamente:
- cria o ambiente virtual do Python e instala as dependências do backend;
- cria o arquivo `.env`;
- inicializa o banco de dados;
- instala as dependências e compila a extensão do VS Code.

> **No Windows?** Use o **Git Bash** (vem com o Git) ou o **WSL** para rodar o `bash install.sh`.
> Se preferir, faça os passos manuais da seção 6.

---

## 🔑 3. Escolher um modelo de IA (obrigatório para respostas reais)

Sem isso, o PedroIA roda mas responde só com uma mensagem de configuração.
**Escolha UMA das duas opções:**

### Opção A — Nuvem (mais fácil, precisa de internet + chave)

Abra o arquivo `backend/.env` e descomente **uma** linha, colando sua chave:

```env
ANTHROPIC_API_KEY=sk-ant-...
# ou:
# OPENAI_API_KEY=sk-...
# GEMINI_API_KEY=...
# DEEPSEEK_API_KEY=...
```

Onde conseguir a chave:
- Anthropic (Claude): https://console.anthropic.com
- OpenAI: https://platform.openai.com/api-keys
- Google Gemini: https://aistudio.google.com/apikey
- DeepSeek: https://platform.deepseek.com

### Opção B — Local / offline (grátis, sem chave, precisa do Ollama)

```bash
# instale o Ollama (https://ollama.com/download), depois:
ollama pull llama3.1                 # modelo de chat
ollama pull qwen2.5-coder:1.5b       # modelo de autocomplete
```

Pronto — o PedroIA detecta o Ollama sozinho quando estiver sem internet
(ou se você definir o modo `local` nas configurações).

---

## ▶️ 4. Ligar o backend

```bash
cd backend
source .venv/bin/activate        # Windows: .venv\Scripts\activate
uvicorn app.main:app --reload
```

Deixe esse terminal **aberto**. Teste no navegador:
- http://127.0.0.1:8000/docs  → documentação da API
- http://127.0.0.1:8000/api/v1/health  → deve responder `{"status":"ok",...}`

---

## 🧩 5. Abrir a extensão no VS Code

### Modo desenvolvimento (recomendado para testar)

```bash
# em outro terminal, na raiz do PedroIA
code extension
```

Com a pasta `extension` aberta no VS Code, pressione **F5**.
Abre uma segunda janela do VS Code (“Extension Development Host”) já com o PedroIA ativo.

Nessa nova janela:
1. Clique no ícone do **PedroIA** na barra lateral esquerda → abre o **chat**.
2. Selecione um trecho de código, clique com o botão direito → menu **PedroIA** (`/explain`, `/fix`…).
3. Comece a digitar código → o **autocomplete** sugere (ghost text).
4. Atalho do chat: **Ctrl+Shift+I** (Mac: Cmd+Shift+I).

### Instalar de vez (gerar o `.vsix`)

```bash
cd extension
npm install -g @vscode/vsce      # uma vez só
vsce package --allow-missing-repository -o pedroia.vsix
code --install-extension pedroia.vsix
```

> Para publicar no Marketplace depois, adicione um `extension/media/icon.png` (128×128).

---

## 🛠️ 6. Passos manuais (alternativa ao install.sh)

<details>
<summary>Clique se preferir fazer sem o install.sh</summary>

**Backend**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate                # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python -c "import asyncio; from app.database.session import init_db; asyncio.run(init_db())"
uvicorn app.main:app --reload
```

**Extensão**
```bash
cd extension
npm install
npm run esbuild
# abra a pasta no VS Code e pressione F5
```
</details>

---

## 🧪 7. Conferir se está tudo certo

```bash
# testes do backend (rodam sem chave, offline)
cd backend && source .venv/bin/activate && pytest
# esperado: 5 passed
```

- Chat responde? ✅ backend + modelo OK
- Autocomplete sugere? ✅ completion OK
- Painel CRM: abra `crm/index.html` no navegador com o backend ligado.

---

## 🐳 8. (Opcional) Rodar com Docker

```bash
cp backend/.env.example backend/.env      # configure suas chaves
docker compose -f docker/docker-compose.yml up --build
# backend em http://localhost:8000, com Postgres e Redis inclusos
```

---

## ❓ Problemas comuns

| Sintoma | Solução |
|--------|---------|
| Chat diz "modo de configuração" | Você ainda não definiu chave nem Ollama — volte ao **passo 3**. |
| "Backend não encontrado" no chat | O backend não está rodando — faça o **passo 4**. Confira a URL em Settings → `pedroia.backendUrl`. |
| `bash: command not found` (Windows) | Use **Git Bash** ou **WSL**, ou siga os passos manuais (seção 6). |
| Autocomplete não aparece | Verifique `pedroia.completion.enabled` em Settings; no modo local, o Ollama precisa estar rodando. |
| Porta 8000 ocupada | Rode `uvicorn app.main:app --reload --port 8001` e ajuste `pedroia.backendUrl` para `http://127.0.0.1:8001`. |
| `pip install` falha | Confirme Python 3.11+ (`python3 --version`) e que o `.venv` está ativado. |

---

## 📚 Próximos passos

- Leia [`README.md`](README.md) para a visão geral.
- Leia [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) para entender a arquitetura e o roadmap.
- Configure o deploy grátis: [`deployment/`](deployment/) (Render/Fly) e `frontend/landing-page/` (Vercel/Netlify).

Bom código! 🤖
