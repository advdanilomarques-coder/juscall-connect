# 🚀 Deploy do backend do PedroIA (Render — grátis)

Este guia te leva de zero até uma URL pública tipo
`https://pedroia-backend.onrender.com`. Tempo: ~10 minutos.

> **Faça o deploy do backend PRIMEIRO.** Sem ele no ar, a extensão publicada não tem a quem se conectar.

---

## Passo 0 — O que você vai precisar

1. Conta no **GitHub** (o código precisa estar num repositório).
2. Conta no **Render** (grátis): https://render.com
3. Uma **chave da Anthropic** (veja o Passo 1).

---

## Passo 1 — Pegar a chave da Anthropic (~3 min)

1. Acesse **https://console.anthropic.com** e crie/entre na sua conta.
2. Adicione crédito em **Billing** (a API é paga por uso; comece com o mínimo, ex.: US$5).
3. Vá em **Settings → API Keys → Create Key**.
4. Copie a chave (formato `sk-ant-api03-...`). **Guarde bem — ela só aparece uma vez.**

> ⚠️ Nunca coloque essa chave na extensão nem no site. Ela fica **só** no backend.

---

## Passo 2 — Subir o código no GitHub

Se o projeto ainda não está no GitHub:

```bash
cd PedroIA
git init
git add .
git commit -m "PedroIA: backend + extensão + site"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/pedroia.git
git push -u origin main
```

---

## Passo 3 — Criar o serviço no Render

### Opção A — pelo Blueprint (usa o `render.yaml`, recomendado)

1. No Render, clique **New → Blueprint**.
2. Conecte o seu repositório do PedroIA.
3. Em **Root Directory**, informe: `PedroIA`
4. O Render lê o `render.yaml` e cria o serviço `pedroia-backend`.

### Opção B — manual (New → Web Service)

- **Root Directory:** `PedroIA/backend`
- **Runtime:** Node
- **Build Command:** `npm install && npm run build`
- **Start Command:** `npm start`
- **Health Check Path:** `/health`
- **Plan:** Free

---

## Passo 4 — Definir as variáveis de ambiente (Environment)

No painel do serviço → **Environment**, adicione:

| Chave | Valor |
|---|---|
| `ANTHROPIC_API_KEY` | a chave `sk-ant-api03-...` do Passo 1 |
| `API_KEYS` | uma chave secreta que você inventa (ex.: gere com `openssl rand -hex 24`) |
| `NODE_ENV` | `production` |
| `PEDROIA_MODEL` | `claude-opus-5` *(opcional)* |
| `RATE_LIMIT_MAX` | `3` *(opcional — quantas req/min por IP)* |

> 🔒 O `API_KEYS` é a chave que a **extensão** vai enviar. Sem ele em produção, o servidor se recusa a subir (proteção contra servidor aberto).
>
> 💡 Já geramos um `API_KEYS` para você no arquivo `backend/.env` local — você pode reutilizá-lo aqui.

Clique **Save Changes**. O Render faz o deploy automaticamente.

---

## Passo 5 — Testar

Quando o deploy terminar, abra no navegador:

```
https://SEU-SERVICO.onrender.com/health
```

Deve responder algo como:

```json
{ "ok": true, "service": "pedroia-backend", "model": "claude-opus-5", "env": "production" }
```

Teste o chat via terminal (troque a URL e a chave):

```bash
curl -N -X POST https://SEU-SERVICO.onrender.com/v1/chat \
  -H "Content-Type: application/json" \
  -H "x-pedroia-key: SUA_API_KEY" \
  -d '{"messages":[{"role":"user","content":"Olá, quem é você?"}]}'
```

Se aparecerem eventos `delta` com texto, está funcionando! ✅

---

## Passo 6 — Anotar a URL

Guarde a URL final (ex.: `https://pedroia-backend.onrender.com`).
Você vai colocá-la na extensão em `extension/package.json`
(campo `pedroia.backendUrl`) e nas configurações do VS Code.

> ⚠️ **Plano free do Render "dorme"** após ~15 min sem uso e demora alguns
> segundos para "acordar" na primeira requisição. Para produção séria,
> considere um plano pago ou outro provedor.

---

## Rodar localmente (opcional, para testar antes)

```bash
cd PedroIA/backend
cp .env.example .env      # e preencha ANTHROPIC_API_KEY
npm install
npm run build
npm start
# → http://localhost:8787/health
```
