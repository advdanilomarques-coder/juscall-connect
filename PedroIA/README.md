<div align="center">

# 🤖 PedroIA

**Seu engenheiro de inteligência artificial dentro do VS Code.**

Chat, autocomplete e comandos que entendem o seu projeto — online ou offline.

[Recursos](#-recursos) · [Instalação](#-instalação-rápida) · [Arquitetura](#-arquitetura) · [Configuração](#-configuração) · [Deploy](#-deploy)

</div>

---

PedroIA é um agente de IA integrado ao VS Code, no estilo GitHub Copilot / Claude Code,
com backend próprio e **roteamento multi-LLM**: usa modelos em nuvem (Claude, OpenAI,
Gemini, DeepSeek) quando há internet e cai automaticamente para **modelos locais via
Ollama** quando está offline.

> Estado atual: **núcleo funcional** — extensão (chat + comandos + autocomplete) e backend
> (roteador multi-LLM, memória, CRM) prontos para rodar localmente. Veja o
> [roadmap](docs/ARCHITECTURE.md#roadmap-técnico).

## ✨ Recursos

- **Chat lateral** com histórico, memória e seleção de modo (Auto / Cloud / Local).
- **Autocomplete inline** (PedroIA Code Completion Engine) — sugestões estilo Copilot.
- **Comandos**: `/create`, `/explain`, `/fix`, `/refactor`, `/test`, `/security` na paleta e no menu de contexto.
- **Contexto automático**: lê arquivo ativo, seleção, diagnósticos e workspace — sem prompts gigantes.
- **Multi-LLM + offline**: Anthropic, OpenAI, Gemini, DeepSeek e Ollama, com cadeia de fallback.
- **Memória** de conversas (SQLAlchemy) e **CRM/monitoramento** de uso e erros.

## 📁 Estrutura

```
PedroIA/
├── extension/        # Extensão VS Code (TypeScript + esbuild)
│   ├── src/
│   │   ├── api/          # cliente HTTP do backend
│   │   ├── chat/         # webview do chat
│   │   ├── completion/   # motor de autocomplete
│   │   ├── commands/     # comandos slash
│   │   └── utils/        # coleta de contexto
│   └── media/            # UI do webview + ícones
├── backend/          # API FastAPI (Python)
│   └── app/
│       ├── api/          # rotas + schemas
│       ├── llm_engine/   # router + providers + prompts
│       ├── memory/       # memória de conversas
│       ├── database/     # modelos SQLAlchemy
│       ├── auth/         # API key opcional
│       └── monitoring/   # logs de uso
├── models/           # docs de modelos locais e em nuvem
├── frontend/
│   └── landing-page/ # landing page (React + Vite + TS)
├── crm/              # painel de monitoramento (HTML)
├── docker/           # Dockerfile + docker-compose
├── deployment/       # render.yaml, fly.toml
├── docs/             # arquitetura
├── install.sh        # instalador automático
├── LICENSE           # MIT
└── README.md
```

## 🚀 Instalação rápida

Pré-requisitos: **Python 3.11+**, **Node.js 18+** e **npm**. (Opcional: VS Code com o comando `code`, e Ollama para modo offline.)

```bash
git clone https://github.com/advdanilomarques-coder/juscall-connect
cd juscall-connect/PedroIA
bash install.sh
```

O `install.sh` cria o ambiente virtual, instala dependências, prepara o `.env`,
inicializa o banco, compila a extensão e (se possível) a instala no VS Code.

### Passo a passo manual

**Backend**
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # configure suas chaves (opcional)
uvicorn app.main:app --reload # http://127.0.0.1:8000/docs
```

**Extensão**
```bash
cd extension
npm install
npm run esbuild               # bundle em dist/
# Abra a pasta no VS Code e pressione F5 (Extension Development Host)
```

## ⚙️ Configuração

No VS Code (**Settings → PedroIA**):

| Chave                          | Padrão                     | Descrição                              |
|--------------------------------|----------------------------|----------------------------------------|
| `pedroia.backendUrl`           | `http://127.0.0.1:8000`    | URL do backend                         |
| `pedroia.apiKey`               | vazio                      | Bearer token (se o backend exigir)     |
| `pedroia.preferredMode`        | `auto`                     | `auto` / `cloud` / `local`             |
| `pedroia.completion.enabled`   | `true`                     | Liga/desliga o autocomplete            |
| `pedroia.completion.debounceMs`| `350`                      | Atraso antes de sugerir                |

No backend (`backend/.env`), defina **pelo menos um** provedor para respostas reais —
veja [models/cloud-models](models/cloud-models/README.md) e
[models/local-models](models/local-models/README.md).

## 🧠 Arquitetura

```
Internet disponível  →  Modelo Cloud (Claude / OpenAI / Gemini / DeepSeek)
Sem internet         →  Modelo Local (Ollama: Llama / Mistral / Qwen)
Nada configurado     →  Fallback (mensagem de configuração)
```

Detalhes e diagramas em [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## 🧪 Testes

```bash
cd backend && source .venv/bin/activate
pip install -r requirements.txt
pytest            # roda offline, sem chaves (usa o provedor de fallback)
```

## 🐳 Docker

```bash
cd PedroIA
cp backend/.env.example backend/.env
docker compose -f docker/docker-compose.yml up --build
# backend em http://localhost:8000 · Postgres + Redis inclusos
```

## ☁️ Deploy

- **Backend**: [Render](deployment/render.yaml) (blueprint incluso) ou [Fly.io](deployment/fly.toml).
- **Landing page**: Vercel/Netlify — configs em `frontend/landing-page/` (`vercel.json`, `netlify.toml`).
- **Banco**: Neon ou Supabase (Postgres gerenciado) — ajuste `DATABASE_URL`.
- **Modelos**: chaves de nuvem por variável de ambiente, ou Ollama local.

## 🤝 Contribuindo

Issues e PRs são bem-vindos. Rode `pytest` (backend) e `npm run lint` (extensão) antes de enviar.

## 📄 Licença

[MIT](LICENSE).
