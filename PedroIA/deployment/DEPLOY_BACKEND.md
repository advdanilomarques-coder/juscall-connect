# ☁️ Hospedar o backend do PedroIA (servidor na nuvem)

Este guia coloca o backend do PedroIA em um **endereço público** (`https://…`), para que
a extensão funcione em **qualquer máquina** sem ninguém precisar rodar Python.

Usaremos o **Render** (tem plano gratuito). O mesmo vale para Fly.io/Railway com pequenos ajustes.

> ⚠️ **Importante (custo):** neste modelo, as chamadas de IA de todos os usuários são cobradas
> na **sua** conta do provedor (OpenAI/Claude/…). O backend já vem com **autenticação por chave**
> e **limite de uso** para você controlar quem acessa e evitar surpresas na fatura.

---

## Pré-requisitos

- Repositório no GitHub (✅ você já tem: `advdanilomarques-coder/juscall-connect`, público).
- Uma conta gratuita no Render: https://render.com (entre com o GitHub).
- **Pelo menos uma** chave de IA (Anthropic, OpenAI, Gemini ou DeepSeek).

---

## Passo a passo (pelo painel do Render)

### 1. Criar o banco de dados
1. No Render, clique em **New → Postgres**.
2. Nome: `pedroia-db` · Plano: **Free** · **Create Database**.
3. Quando pronto, copie a **Internal Database URL** (começa com `postgresql://…`). Guarde.

### 2. Criar o serviço web (o backend)
1. **New → Web Service** → conecte o repositório `juscall-connect`.
2. Configure:
   - **Root Directory:** `PedroIA`  ← **essencial** (o projeto está nessa subpasta)
   - **Runtime / Environment:** `Docker`
   - **Dockerfile Path:** `docker/backend.Dockerfile`
   - **Branch:** `claude/pedroia-vscode-extension-tq50xm` (ou `main`, depois do merge)
   - **Plan:** Free
3. Em **Advanced → Health Check Path**, coloque: `/api/v1/health`

### 3. Definir as variáveis de ambiente (Environment)
Adicione (aba **Environment → Add Environment Variable**):

| Chave                 | Valor                                                        |
|-----------------------|-------------------------------------------------------------|
| `ENVIRONMENT`         | `production`                                                |
| `DEBUG`               | `false`                                                     |
| `DATABASE_URL`        | *cole a URL do passo 1, trocando* `postgresql://` *por* `postgresql+asyncpg://` |
| `API_KEYS`            | uma senha forte que você inventa (ex.: `pedroia_a1b2c3...`) — é a **chave de acesso** dos usuários |
| `ANTHROPIC_API_KEY`   | sua chave (ou use `OPENAI_API_KEY` / `GEMINI_API_KEY` / `DEEPSEEK_API_KEY`) |

> 🔑 Sobre `DATABASE_URL`: o backend usa driver assíncrono. Garanta o prefixo
> `postgresql+asyncpg://…`. Se você usar o driver `asyncpg`, descomente a linha
> `asyncpg` em `backend/requirements.txt` **ou** o Render instala pelo Docker normalmente.

### 4. Publicar
1. Clique em **Create Web Service**. O Render faz o build do Docker e sobe o serviço.
2. Ao terminar, você recebe uma URL pública, algo como:
   `https://pedroia-backend.onrender.com`
3. Teste no navegador: `https://SEU-SERVICO.onrender.com/api/v1/health`
   → deve responder `{"status":"ok",...}`.

---

## Alternativa rápida: Blueprint (render.yaml)

Já existe um `deployment/render.yaml` pronto. No Render: **New → Blueprint**, aponte para o
repositório e ele cria o serviço + banco automaticamente. Depois, adicione as chaves de IA
na aba **Environment** (elas não ficam no arquivo por segurança).

---

## Conectar a extensão ao servidor

Depois que o backend estiver no ar, cada usuário configura no VS Code
(**Settings → PedroIA**):

- `pedroia.backendUrl` = `https://SEU-SERVICO.onrender.com`
- `pedroia.apiKey` = o valor que você colocou em `API_KEYS`

> 💡 Para já publicar a extensão com o endereço certo por padrão, edite
> `extension/package.json` → `pedroia.backendUrl` → `"default"` com a sua URL,
> antes de empacotar (veja `PUBLICAR.md`).

---

## Notas de custo e escala

- **Render Free** hiberna após inatividade — a primeira chamada depois disso demora alguns segundos.
  Para uso sério, suba para um plano pago pequeno ou use Fly.io.
- O **rate limit** padrão é 30 req/min e 1000 req/dia por usuário
  (ajuste com `RATE_LIMIT_PER_MINUTE` / `RATE_LIMIT_PER_DAY`).
- Distribua a `API_KEYS` só para quem você quer que use — assim controla o consumo.
- Para vários usuários com chaves diferentes, use uma lista separada por vírgula em `API_KEYS`.
