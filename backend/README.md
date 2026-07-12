# Marques IA — Backend (Etapa 1: Ambiente + Camada de IA)

Sistema de IA jurídica para atendimento via WhatsApp. Esta é a **primeira
etapa**: montamos o ambiente profissional em Python e a peça central da
arquitetura — a **Camada de Abstração de IA** (com failover automático entre
modelos). As próximas etapas (WhatsApp, CRM, PostgreSQL) serão construídas
sobre esta fundação.

---

## 1. Objetivo desta etapa

- Criar a estrutura de pastas e arquivos do projeto.
- Configurar o ambiente virtual e as dependências.
- Implementar a camada de IA desacoplada (Claude como principal, GPT como
  reserva), seguindo SOLID, Clean Architecture e Clean Code.
- Deixar uma API rodando com um endpoint de conversa (`/chat`).

---

## 2. Pré-requisitos

- **Python 3.11+** — confira com `python3 --version`
- Uma **chave de API da Anthropic** (Claude). A da OpenAI é opcional.

---

## 3. Estrutura de diretórios

```
backend/
├── .env.example            # Modelo das variáveis de ambiente (copie p/ .env)
├── .gitignore              # Ignora .env, .venv, caches...
├── requirements.txt        # Dependências (versões fixadas)
├── pytest.ini              # Configuração dos testes
├── setup.sh                # Script que automatiza a preparação do ambiente
├── README.md               # Este guia
│
├── app/                    # Código-fonte da aplicação
│   ├── __init__.py
│   ├── main.py             # Ponto de entrada (API FastAPI)
│   │
│   ├── core/               # Infraestrutura transversal (sem regra de negócio)
│   │   ├── __init__.py
│   │   ├── config.py       # Configuração via .env (tipada e validada)
│   │   ├── logging.py      # Logs estruturados
│   │   └── exceptions.py   # Exceções de domínio
│   │
│   └── ai/                 # CAMADA DE ABSTRAÇÃO DE IA (o coração)
│       ├── __init__.py
│       ├── schemas.py      # Contratos de entrada/saída padronizados
│       ├── base.py         # Interface abstrata AIProvider
│       ├── manager.py      # AIManager: orquestra provedores + failover
│       └── providers/      # Implementações concretas
│           ├── __init__.py
│           ├── claude_provider.py   # Modelo principal (Claude)
│           └── openai_provider.py   # Modelo reserva (GPT)
│
└── tests/                  # Testes automatizados
    ├── __init__.py
    └── test_ai_manager.py  # Testa o failover sem gastar tokens
```

### Por que essa organização?

- **Cada arquivo tem uma única responsabilidade** (Princípio da Responsabilidade Única).
- **`core/`** contém infraestrutura reutilizável (config, logs, erros).
- **`ai/`** isola 100% da comunicação com modelos de IA. As regras de negócio
  (CRM, jurídico) nunca falam com Claude/GPT diretamente — falam com o
  `AIManager`. Trocar de modelo = criar um novo Provider, sem tocar no resto.

---

## 4. Passo a passo — criando o ambiente do zero

Você pode rodar o script automático **ou** seguir os comandos manualmente.

### Opção A — script automático

```bash
cd backend
bash setup.sh
```

### Opção B — passo a passo manual (recomendado para entender cada etapa)

**Passo 1 — entre na pasta do backend:**

```bash
cd backend
```

**Passo 2 — crie o ambiente virtual** (isola as dependências deste projeto):

```bash
python3 -m venv .venv
```

**Passo 3 — ative o ambiente virtual:**

```bash
# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

**Passo 4 — atualize o pip e instale as dependências:**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Passo 5 — crie seu arquivo de configuração a partir do modelo:**

```bash
cp .env.example .env
```

**Passo 6 — edite o `.env`** e coloque sua chave da Anthropic:

```
ANTHROPIC_API_KEY="sk-ant-sua-chave-aqui"
```

**Passo 7 — rode os testes** (comprova que a camada de IA funciona):

```bash
pytest
```

**Passo 8 — suba a aplicação:**

```bash
uvicorn app.main:app --reload
```

A API estará em `http://127.0.0.1:8000`.
Documentação interativa automática em `http://127.0.0.1:8000/docs`.

---

## 5. Testando a API

**Healthcheck:**

```bash
curl http://127.0.0.1:8000/
```

**Mensagem inicial obrigatória do atendimento:**

```bash
curl http://127.0.0.1:8000/initial-message
```

**Conversar com o agente:**

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Meu carro foi apreendido, o que eu faço?"}'
```

Resposta (exemplo):

```json
{
  "reply": "Sinto muito por essa situação...",
  "provider": "claude",
  "model": "claude-opus-4-8"
}
```

---

## 6. Como o failover funciona

1. A ordem dos modelos vem do `.env` (`AI_PROVIDER_ORDER="claude,openai"`).
2. O `AIManager` tenta o **Claude** primeiro.
3. Se o Claude falhar (timeout/erro/indisponibilidade), ele registra o erro e
   **alterna automaticamente para o GPT** — o cliente nunca percebe.
4. Se todos falharem, a API responde com uma mensagem amigável de fallback
   (nunca um erro técnico).

---

## 7. Como adicionar um novo modelo (ex.: Gemini)

Graças à camada de abstração, você **não altera** o CRM, o atendimento nem
o `main.py`. Basta:

1. Criar `app/ai/providers/gemini_provider.py` implementando `AIProvider`.
2. Registrá-lo em `app/ai/manager.py` no dicionário `_PROVIDER_REGISTRY`.
3. Adicionar `gemini` ao `AI_PROVIDER_ORDER` no `.env`.

Isso é o Princípio Aberto/Fechado do SOLID na prática.

---

## 8. Próximas etapas do projeto

- [ ] Memória persistente (PostgreSQL) — histórico independente do modelo.
- [ ] Webhook do WhatsApp Business + QR Code de conexão.
- [ ] CRM (leads, funil, contratos, documentos).
- [ ] Geração automática de contratos em PDF.
- [ ] Painel administrativo e controle de custos por tokens.
- [ ] Segurança (JWT, LGPD, rate limit).
