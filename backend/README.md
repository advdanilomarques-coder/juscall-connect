# Marques IA — Backend (Agente de IA Jurídico)

Sistema de atendimento automático por IA para escritórios de advocacia,
especializado em Direito Bancário e do Consumidor. Backend em **Python +
FastAPI**, seguindo SOLID, Clean Architecture e camadas desacopladas.

> Este backend é a evolução da arquitetura base gerada pelo instalador
> (`instalar_marques_ia.sh`): agora com CRM completo, geração de contratos,
> múltiplos provedores de IA, WhatsApp, segurança JWT e painel administrativo.

---

## 1. Visão geral da arquitetura

```
                        ┌──────────────────────────────────────────┐
   Canais               │                 FastAPI                   │
 (WhatsApp,   ─────────▶│  /chat  /channels  /admin  /crm           │
  site,widget)          │  /documents  /contracts                   │
                        └───────────────┬──────────────────────────┘
                                        │
                        ┌───────────────▼───────────────┐
                        │        Serviço de Memória       │  ← une tudo
                        │  (histórico + contexto + IA)    │
                        └───────┬───────────────┬─────────┘
                                │               │
                ┌───────────────▼──┐     ┌──────▼────────────────────┐
                │   Camada de IA    │     │   Banco de Dados (ORM)     │
                │   (AIManager)     │     │  leads, conversas, msgs,   │
                │  failover+retry+  │     │  documentos, contratos,    │
                │  roteamento+custo │     │  tarefas, notas, custos    │
                └───┬───────────────┘     └────────────────────────────┘
                    │
   ┌────────────────┼───────────────────────────────────────────┐
   │ Providers (Aberto/Fechado): claude, gemini, openai,         │
   │ deepseek, mistral, openrouter, grok, ollama, ...            │
   └─────────────────────────────────────────────────────────────┘
```

**Princípio central:** nenhuma regra de negócio fala diretamente com um modelo
de IA. Tudo passa pela **Camada de IA (`AIManager`)**. Trocar/adicionar um
modelo = criar um novo *Provider*, sem mexer no resto do sistema.

---

## 2. Estrutura de diretórios

```
backend/
├── app/
│   ├── core/          # config, logging, exceções, segurança (JWT/hash), rate limit
│   ├── ai/            # CAMADA DE IA: schemas, base, manager, pricing
│   │   └── providers/ # claude, gemini, openai, deepseek, mistral, openrouter, grok, ollama
│   ├── db/            # engine SQLAlchemy async + modelos ORM (memória + CRM)
│   ├── memory/        # repositório + serviço (une persistência e IA)
│   ├── chat/          # personalidade do agente (prompt) + endpoint de atendimento
│   ├── channels/      # abstração multicanal + WhatsApp Business API
│   ├── crm/           # funil/kanban, leads, tarefas, anotações
│   ├── documents/     # upload e organização de arquivos por cliente/data/tipo
│   ├── contracts/     # modelos de contrato + geração automática em PDF
│   ├── admin/         # login, dashboard, custos, supervisão de conversas
│   ├── deps.py        # dependências FastAPI (sessão, admin autenticado, rate limit)
│   └── main.py        # ponto de entrada: integra todos os módulos
├── tests/             # testes de IA (failover/retry/roteamento), memória, CRM, contratos
├── requirements.txt
├── .env.example
└── setup.sh
```

Cada arquivo tem **uma única responsabilidade** e docstrings explicando o *porquê*.

---

## 3. Instalação e execução

```bash
cd backend
bash setup.sh                 # cria .venv, instala dependências e prepara o .env
source .venv/bin/activate
# edite o .env e coloque pelo menos UMA chave de IA
uvicorn app.main:app --reload
```

- Documentação interativa (Swagger): **http://localhost:8000/docs**
- Healthcheck: **http://localhost:8000/**

> **Não precisa de Docker.** O padrão usa **SQLite** (arquivo local) e um rate
> limiter em memória. Para produção, basta trocar `DATABASE_URL` para
> PostgreSQL no `.env` — nenhuma linha de código muda.

### Chave de IA gratuita para começar
O Google Gemini oferece uma chave **gratuita** (sem cartão):
https://aistudio.google.com/apikey — cole em `GEMINI_API_KEY` e ajuste
`AI_PROVIDER_ORDER="gemini,..."`.

---

## 4. Principais endpoints

| Método | Rota | Descrição | Auth |
|---|---|---|---|
| GET  | `/` | Status da aplicação | — |
| GET  | `/chat/initial-message` | Mensagem inicial obrigatória | — |
| POST | `/chat` | Conversa com memória (site/widget) | — |
| GET/POST | `/channels/whatsapp/webhook` | Webhook do WhatsApp Business | — |
| POST | `/admin/login` | Login → token JWT | — |
| GET  | `/admin/dashboard` | Números gerais do escritório | JWT |
| GET  | `/admin/usage` | Custos/tokens por provedor de IA | JWT |
| POST | `/admin/reply` | Admin responde manualmente | JWT |
| GET  | `/crm/kanban` | Quadro kanban do funil | JWT |
| GET/PATCH | `/crm/leads/...` | Leads, status, notas, tarefas | JWT |
| POST | `/documents/leads/{id}` | Upload de documento | JWT |
| POST | `/contracts/leads/{id}` | Gerar contrato em PDF | JWT |

O **admin inicial** é criado no primeiro startup a partir de `ADMIN_EMAIL` /
`ADMIN_PASSWORD` do `.env`.

---

## 5. Como os requisitos do projeto foram atendidos

- **Camada de IA desacoplada** com *failover* automático, *retry* com backoff,
  roteamento por tipo de tarefa e controle de custos (tokens/valor/latência).
- **8 provedores** prontos (Claude, Gemini, OpenAI, DeepSeek, Mistral,
  OpenRouter, Grok, Ollama). Adicionar outro = uma classe nova.
- **Memória unificada** no banco, independente do modelo: a troca de IA nunca
  faz o agente esquecer o histórico do cliente.
- **CRM** com as 12 etapas do funil, kanban, tarefas e anotações.
- **Documentos** organizados por cliente/data/tipo.
- **Contratos** gerados automaticamente em PDF.
- **Segurança**: JWT, hash de senha (PBKDF2), rate limit, CORS, proteção do
  painel; SQL Injection mitigado pelo ORM (consultas parametrizadas).
- **Testes automatizados** cobrindo failover, retry, roteamento, memória, CRM
  e geração de contratos.

---

## 6. Testes

```bash
source .venv/bin/activate
pytest -q
```

Os testes usam provedores de IA *falsos* e um banco SQLite temporário — não
gastam tokens nem dependem de rede.

---

## 7. Próximos passos sugeridos

- Migrações versionadas com **Alembic** (hoje as tabelas são criadas via
  `create_all`, ideal para dev; Alembic é o próximo passo para produção).
- Fila assíncrona (ex.: **Redis + worker**) para processar mídia/áudio.
- Canais adicionais (Telegram, Instagram) — basta um novo `ChannelClient`.
- Transcrição de áudio (Whisper) e OCR de documentos (Vision).
