# Marques IA — Guia Completo de Implementação (Backend)

> Sistema de IA jurídica para atendimento via WhatsApp.
> Este guia contém **TODO o código pronto para copiar e colar**, na ordem
> correta, mais o passo a passo e o que fazer depois de tudo pronto.

Cobre duas etapas já construídas e testadas:

- **Etapa 1 — Ambiente + Camada de IA:** fundação em Python + Camada de
  Abstração de IA com failover automático (Claude principal, GPT reserva).
- **Etapa 2 — Memória Persistente:** o agente lembra de tudo (leads,
  conversas, histórico), de forma independente do modelo de IA. Preparado
  para PostgreSQL, com SQLite como padrão local.

---

## 1. Pré-requisitos

- **Python 3.11 ou superior** — confira com `python3 --version`
- Uma **chave de API da Anthropic** (Claude). A da OpenAI é opcional (reserva).

---

## 2. Estrutura de pastas e arquivos

Crie a pasta `backend/` (dentro do seu projeto) com esta estrutura:

```
backend/
├── .env.example            # Modelo das variáveis de ambiente (copie p/ .env)
├── .gitignore              # Ignora .env, .venv, banco local, caches...
├── requirements.txt        # Dependências (versões fixadas)
├── pytest.ini              # Configuração dos testes
├── setup.sh                # Script que automatiza a preparação do ambiente
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
│   ├── ai/                 # CAMADA DE ABSTRAÇÃO DE IA (o coração)
│   │   ├── __init__.py
│   │   ├── schemas.py      # Contratos de entrada/saída padronizados
│   │   ├── base.py         # Interface abstrata AIProvider
│   │   ├── manager.py      # AIManager: orquestra provedores + failover
│   │   └── providers/      # Implementações concretas
│   │       ├── __init__.py
│   │       ├── claude_provider.py   # Modelo principal (Claude)
│   │       └── openai_provider.py   # Modelo reserva (GPT)
│   │
│   ├── db/                 # PERSISTÊNCIA (memória do agente)
│   │   ├── __init__.py
│   │   ├── base.py         # Engine, sessões e init_db (SQLite/PostgreSQL)
│   │   └── models.py       # Tabelas: Lead, Conversation, Message
│   │
│   └── memory/             # CAMADA DE MEMÓRIA (une banco + IA)
│       ├── __init__.py
│       ├── repository.py   # Acesso ao banco (padrão Repository)
│       └── service.py      # MemoryService: histórico + IA + persistência
│
└── tests/                  # Testes automatizados
    ├── __init__.py
    ├── test_ai_manager.py  # Testa o failover sem gastar tokens
    └── test_memory.py      # Testa a persistência do histórico
```

### Comandos para criar as pastas de uma vez

```bash
mkdir -p backend/app/core
mkdir -p backend/app/ai/providers
mkdir -p backend/app/db
mkdir -p backend/app/memory
mkdir -p backend/tests
cd backend
```

---

## 3. Código de cada arquivo (copiar e colar)

Crie cada arquivo abaixo com **exatamente** o conteúdo mostrado.

### Arquivo: `backend/requirements.txt`
```text
# ============================================================================
# DEPENDÊNCIAS DO PROJETO — MARQUES IA (Backend)
# ----------------------------------------------------------------------------
# Cada dependência tem uma única responsabilidade. Versões fixadas (pinned)
# garantem builds reproduzíveis em qualquer máquina/servidor.
# ============================================================================

# --- Framework web assíncrono (API REST + webhooks do WhatsApp) ---
fastapi==0.115.6
uvicorn[standard]==0.34.0

# --- Configuração por variáveis de ambiente (.env), com validação de tipos ---
pydantic==2.10.4
pydantic-settings==2.7.1
python-dotenv==1.0.1

# --- SDKs oficiais dos provedores de IA (Camada AI Provider) ---
anthropic==0.42.0        # Modelo principal: Claude
openai==1.59.6           # Modelo secundário/failover: GPT

# --- Cliente HTTP assíncrono (usado por provedores REST genéricos) ---
httpx==0.28.1

# --- Banco de dados / ORM (memória persistente) ---
# SQLAlchemy async funciona tanto com PostgreSQL (asyncpg) quanto com
# SQLite (aiosqlite). Trocar de banco = trocar apenas a DATABASE_URL.
sqlalchemy==2.0.36
aiosqlite==0.20.0        # driver SQLite (padrão local/desenvolvimento)
asyncpg==0.30.0          # driver PostgreSQL (produção)
greenlet==3.1.1          # requisito do modo assíncrono do SQLAlchemy

# --- Testes automatizados ---
pytest==8.3.4
pytest-asyncio==0.25.2

```

### Arquivo: `backend/.env.example`
```bash
# ============================================================================
# ARQUIVO DE EXEMPLO DE VARIÁVEIS DE AMBIENTE
# ----------------------------------------------------------------------------
# Copie este arquivo para `.env` e preencha com seus valores reais.
# NUNCA comite o arquivo `.env` (ele contém segredos). Veja o .gitignore.
#
#   cp .env.example .env
# ============================================================================

# --- Identificação da aplicação ---
APP_NAME="Marques IA"
APP_ENV="development"          # development | production
DEBUG="true"

# --- Chaves das APIs de IA (Camada AI Provider) ---
# Modelo principal (Claude / Anthropic)
ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxxxxxxxxxxxxx"

# Modelo secundário / failover (GPT / OpenAI) — opcional
OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"

# --- Seleção e ordem de failover dos modelos ---
# O sistema tenta os provedores nesta ordem. Se o primeiro falhar,
# alterna automaticamente para o próximo (sem o cliente perceber).
AI_PROVIDER_ORDER="claude,openai"

# Modelos específicos por provedor
CLAUDE_MODEL="claude-opus-4-8"
OPENAI_MODEL="gpt-4o"

# --- Parâmetros de geração ---
AI_MAX_TOKENS="1024"

# --- Banco de dados (memória persistente) ---
# Padrão local (SQLite — não precisa instalar nada):
DATABASE_URL="sqlite+aiosqlite:///./storage/marques_ia.db"
# Em produção, troque por PostgreSQL:
# DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/marques_ia"

# --- Logs ---
LOG_LEVEL="INFO"              # DEBUG | INFO | WARNING | ERROR

```

### Arquivo: `backend/.gitignore`
```gitignore
# ==== Segredos — NUNCA comitar ====
.env

# ==== Ambiente virtual Python ====
.venv/
venv/
env/

# ==== Cache/artefatos do Python ====
__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/
.mypy_cache/
.ruff_cache/

# ==== Logs e dados locais ====
*.log
storage/

```

### Arquivo: `backend/pytest.ini`
```ini
[pytest]
# Habilita testes assíncronos automaticamente (não precisa marcar cada um).
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
testpaths = tests

```

### Arquivo: `backend/setup.sh`
```bash
#!/usr/bin/env bash
# ============================================================================
# SCRIPT DE PREPARAÇÃO DO AMBIENTE — MARQUES IA (Backend)
# ----------------------------------------------------------------------------
# Automatiza os passos manuais: cria o ambiente virtual, instala as
# dependências e prepara o arquivo .env.
#
# Uso:
#   cd backend
#   bash setup.sh
# ============================================================================
set -euo pipefail

echo "==> 1/4 Criando ambiente virtual (.venv)..."
python3 -m venv .venv

echo "==> 2/4 Ativando ambiente virtual..."
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> 3/4 Instalando dependências (requirements.txt)..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> 4/4 Preparando arquivo .env..."
if [ ! -f .env ]; then
  cp .env.example .env
  echo "    .env criado a partir de .env.example — preencha suas chaves de API."
else
  echo "    .env já existe — mantido."
fi

echo ""
echo "Ambiente pronto! Próximos passos:"
echo "  1) Edite o arquivo .env e coloque sua ANTHROPIC_API_KEY."
echo "  2) source .venv/bin/activate"
echo "  3) uvicorn app.main:app --reload"

```

### Arquivo: `backend/app/__init__.py`
```python
"""Pacote raiz da aplicação Marques IA (backend).

Marca o diretório `app/` como um pacote Python, permitindo imports
absolutos como `from app.core.config import settings`.
"""

```

### Arquivo: `backend/app/core/__init__.py`
```python
"""Núcleo transversal da aplicação: configuração, logging e exceções.

Este pacote contém código de infraestrutura usado por todas as demais
camadas (IA, CRM, atendimento). Não depende de regras de negócio.
"""

```

### Arquivo: `backend/app/core/config.py`
```python
"""Configuração centralizada da aplicação.

Toda configuração vem de variáveis de ambiente (arquivo `.env`), seguindo a
prática dos "12 Factor App". Assim, o mesmo código roda em desenvolvimento e
em produção mudando apenas o ambiente — nunca o código-fonte.

`pydantic-settings` faz a leitura do `.env`, valida os tipos e expõe um
objeto `settings` já pronto e tipado para o resto do sistema.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Modelo tipado de todas as configurações da aplicação."""

    # Diz ao pydantic para ler o arquivo `.env` e ignorar variáveis extras.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Identificação da aplicação ---
    app_name: str = "Marques IA"
    app_env: str = "development"
    debug: bool = True

    # --- Chaves das APIs de IA ---
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # --- Seleção e ordem de failover dos provedores de IA ---
    # Ex.: "claude,openai" — o primeiro é o principal; os demais são reserva.
    ai_provider_order: str = "claude,openai"
    claude_model: str = "claude-opus-4-8"
    openai_model: str = "gpt-4o"
    ai_max_tokens: int = 1024

    # --- Banco de dados (memória persistente) ---
    # Padrão SQLite local; em produção use PostgreSQL via .env.
    database_url: str = "sqlite+aiosqlite:///./storage/marques_ia.db"

    # --- Logs ---
    log_level: str = "INFO"

    @property
    def provider_order(self) -> list[str]:
        """Converte "claude,openai" em ["claude", "openai"] já normalizado."""
        return [p.strip().lower() for p in self.ai_provider_order.split(",") if p.strip()]


@lru_cache
def get_settings() -> Settings:
    """Retorna uma única instância de Settings (cacheada) para toda a app.

    O `lru_cache` garante que o `.env` seja lido apenas uma vez, evitando
    releitura de disco a cada requisição.
    """
    return Settings()


# Instância global pronta para importar em qualquer módulo:
#   from app.core.config import settings
settings = get_settings()

```

### Arquivo: `backend/app/core/logging.py`
```python
"""Configuração de logs estruturados.

Um sistema comercial precisa de logs claros para auditoria, depuração e
monitoramento. Aqui centralizamos a configuração para que todo o projeto
use o mesmo formato de log.
"""

from __future__ import annotations

import logging

from app.core.config import settings


def setup_logging() -> None:
    """Configura o logger raiz uma única vez, no início da aplicação."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def get_logger(name: str) -> logging.Logger:
    """Retorna um logger nomeado para o módulo que o solicita.

    Uso típico:
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        logger.info("mensagem")
    """
    return logging.getLogger(name)

```

### Arquivo: `backend/app/core/exceptions.py`
```python
"""Exceções de domínio da aplicação.

Definir exceções próprias (em vez de usar apenas as genéricas do Python)
deixa o tratamento de erros explícito e permite reagir de forma diferente
a cada tipo de falha — essencial para o failover automático da IA.
"""

from __future__ import annotations


class MarquesIAError(Exception):
    """Exceção base — toda exceção do projeto herda desta."""


class AIProviderError(MarquesIAError):
    """Falha ao chamar um provedor de IA específico (timeout, erro de API...).

    Quando o gerenciador de IA captura esta exceção, ele tenta o próximo
    provedor da lista de failover.
    """


class AllProvidersFailedError(MarquesIAError):
    """Todos os provedores de IA falharam — nenhum conseguiu responder."""


class ProviderNotConfiguredError(MarquesIAError):
    """Um provedor foi solicitado mas não tem chave de API configurada."""

```

### Arquivo: `backend/app/ai/__init__.py`
```python
"""Camada de Abstração de IA (AI Provider Layer).

Esta é a peça central da arquitetura descrita no documento do projeto.

Toda comunicação com modelos de IA passa EXCLUSIVAMENTE por esta camada.
As regras de negócio (CRM, atendimento, jurídico) nunca falam diretamente
com Claude, GPT ou qualquer outro modelo — elas falam com o `AIManager`.

Benefícios (Princípio da Inversão de Dependência — o "D" do SOLID):
  * Trocar/adicionar modelos = criar um novo Provider, sem tocar no resto.
  * Failover automático entre modelos.
  * Memória e regras de negócio ficam independentes do modelo de IA.
"""

```

### Arquivo: `backend/app/ai/schemas.py`
```python
"""Contratos de dados (schemas) da camada de IA.

Estes tipos padronizam o formato de entrada e saída, INDEPENDENTE do modelo
usado. Assim, quem chama a IA sempre recebe a mesma estrutura, seja a
resposta vinda do Claude, do GPT ou de qualquer outro provedor futuro.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Role(str, Enum):
    """Papéis possíveis numa conversa (padrão de mercado)."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class AIMessage:
    """Uma única mensagem da conversa (entrada padronizada)."""

    role: Role
    content: str


@dataclass
class AIResponse:
    """Resposta padronizada devolvida pela camada de IA (saída padronizada).

    Note que ela carrega metadados (`provider`, `model`, tokens) usados para
    controle de custos e para informar ao administrador qual modelo respondeu.
    """

    content: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    raw: dict = field(default_factory=dict)

```

### Arquivo: `backend/app/ai/base.py`
```python
"""Interface abstrata que todo provedor de IA deve implementar.

Este é o "contrato" da Camada AI Provider. Qualquer modelo novo (Gemini,
DeepSeek, Mistral, Llama, Ollama...) só precisa criar uma classe que herde
de `AIProvider` e implemente `generate()`. Nenhuma outra parte do sistema
precisa mudar — é o Princípio Aberto/Fechado (o "O" do SOLID) em ação.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.ai.schemas import AIMessage, AIResponse


class AIProvider(ABC):
    """Classe base abstrata para todos os provedores de IA."""

    #: Nome curto do provedor (ex.: "claude", "openai"). Usado nos logs e
    #: na ordem de failover definida no `.env`.
    name: str = "base"

    @abstractmethod
    async def generate(
        self,
        messages: list[AIMessage],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> AIResponse:
        """Envia as mensagens ao modelo e retorna uma resposta padronizada.

        Args:
            messages: histórico da conversa já no formato padrão.
            system: instrução de sistema (personalidade/regras do agente).
            max_tokens: limite de tokens da resposta.

        Returns:
            AIResponse padronizado.

        Raises:
            AIProviderError: se a chamada ao modelo falhar.
        """
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """Indica se o provedor está pronto para uso (ex.: tem chave de API)."""
        raise NotImplementedError

```

### Arquivo: `backend/app/ai/providers/__init__.py`
```python
"""Implementações concretas de provedores de IA.

Cada arquivo aqui implementa a interface `AIProvider` para um modelo
específico. Adicionar um novo modelo = adicionar um novo arquivo aqui.
"""

```

### Arquivo: `backend/app/ai/providers/claude_provider.py`
```python
"""Provedor de IA: Claude (Anthropic) — modelo PRINCIPAL do sistema.

Implementa a interface `AIProvider` usando o SDK oficial da Anthropic.
Modelo padrão: `claude-opus-4-8`.
"""

from __future__ import annotations

import anthropic

from app.ai.base import AIProvider
from app.ai.schemas import AIMessage, AIResponse, Role
from app.core.config import settings
from app.core.exceptions import AIProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)


class ClaudeProvider(AIProvider):
    """Provedor que conversa com os modelos Claude da Anthropic."""

    name = "claude"

    def __init__(self) -> None:
        # Cliente assíncrono; se não houver chave, ele fica None e o provedor
        # se reporta como indisponível (usado no failover).
        self._api_key = settings.anthropic_api_key
        self._model = settings.claude_model
        self._client = (
            anthropic.AsyncAnthropic(api_key=self._api_key) if self._api_key else None
        )

    def is_available(self) -> bool:
        """Só está disponível se houver chave de API configurada."""
        return self._client is not None

    async def generate(
        self,
        messages: list[AIMessage],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> AIResponse:
        if self._client is None:
            raise AIProviderError("Claude sem ANTHROPIC_API_KEY configurada.")

        # Converte o histórico padronizado para o formato do SDK da Anthropic.
        # A mensagem de sistema NÃO entra na lista `messages` — vai no campo
        # `system` separado (regra da API da Anthropic).
        api_messages = [
            {"role": m.role.value, "content": m.content}
            for m in messages
            if m.role != Role.SYSTEM
        ]

        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                system=system or anthropic.NOT_GIVEN,
                messages=api_messages,
            )
        except anthropic.APIError as exc:
            # Encapsula o erro do SDK na nossa exceção de domínio para que o
            # gerenciador consiga acionar o failover.
            logger.warning("Falha no provedor Claude: %s", exc)
            raise AIProviderError(f"Claude falhou: {exc}") from exc

        # A resposta pode conter vários blocos; juntamos apenas os de texto.
        text = "".join(block.text for block in response.content if block.type == "text")

        return AIResponse(
            content=text,
            provider=self.name,
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )

```

### Arquivo: `backend/app/ai/providers/openai_provider.py`
```python
"""Provedor de IA: GPT (OpenAI) — modelo SECUNDÁRIO / de failover.

Serve como reserva: se o Claude ficar indisponível, o gerenciador alterna
automaticamente para este provedor, sem o cliente perceber a troca.
"""

from __future__ import annotations

from openai import AsyncOpenAI, OpenAIError

from app.ai.base import AIProvider
from app.ai.schemas import AIMessage, AIResponse, Role
from app.core.config import settings
from app.core.exceptions import AIProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIProvider(AIProvider):
    """Provedor que conversa com os modelos GPT da OpenAI."""

    name = "openai"

    def __init__(self) -> None:
        self._api_key = settings.openai_api_key
        self._model = settings.openai_model
        self._client = (
            AsyncOpenAI(api_key=self._api_key) if self._api_key else None
        )

    def is_available(self) -> bool:
        return self._client is not None

    async def generate(
        self,
        messages: list[AIMessage],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> AIResponse:
        if self._client is None:
            raise AIProviderError("OpenAI sem OPENAI_API_KEY configurada.")

        # Na OpenAI a instrução de sistema é uma mensagem com role="system"
        # no início da lista.
        api_messages: list[dict] = []
        if system:
            api_messages.append({"role": Role.SYSTEM.value, "content": system})
        api_messages.extend(
            {"role": m.role.value, "content": m.content} for m in messages
        )

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                max_tokens=max_tokens,
                messages=api_messages,
            )
        except OpenAIError as exc:
            logger.warning("Falha no provedor OpenAI: %s", exc)
            raise AIProviderError(f"OpenAI falhou: {exc}") from exc

        choice = response.choices[0]
        usage = response.usage

        return AIResponse(
            content=choice.message.content or "",
            provider=self.name,
            model=response.model,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
        )

```

### Arquivo: `backend/app/ai/manager.py`
```python
"""Gerenciador de IA (AIManager) — orquestra os provedores com failover.

É o único ponto de entrada para o resto do sistema pedir uma resposta de IA.
Responsabilidades (conforme o documento do projeto):
  * Enviar a pergunta ao modelo principal.
  * Em caso de erro/indisponibilidade, alternar automaticamente para o
    próximo modelo da lista (failover).
  * Registrar qual modelo respondeu (para o painel administrativo).
  * Nunca informar o cliente sobre a troca — o atendimento não pode parar.
"""

from __future__ import annotations

from app.ai.base import AIProvider
from app.ai.providers.claude_provider import ClaudeProvider
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.schemas import AIMessage, AIResponse
from app.core.config import settings
from app.core.exceptions import AIProviderError, AllProvidersFailedError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Registro de provedores conhecidos. Para adicionar um modelo novo, basta
# implementar um Provider e registrá-lo aqui (mais o nome no AI_PROVIDER_ORDER).
_PROVIDER_REGISTRY: dict[str, type[AIProvider]] = {
    "claude": ClaudeProvider,
    "openai": OpenAIProvider,
}


class AIManager:
    """Seleciona e executa provedores de IA na ordem configurada."""

    def __init__(self) -> None:
        # Instancia os provedores na ordem definida em AI_PROVIDER_ORDER.
        self._providers: list[AIProvider] = []
        for provider_name in settings.provider_order:
            provider_cls = _PROVIDER_REGISTRY.get(provider_name)
            if provider_cls is None:
                logger.warning("Provedor desconhecido ignorado: %s", provider_name)
                continue
            self._providers.append(provider_cls())

    async def generate(
        self,
        messages: list[AIMessage],
        *,
        system: str | None = None,
        max_tokens: int | None = None,
    ) -> AIResponse:
        """Tenta cada provedor em ordem até um responder com sucesso.

        Raises:
            AllProvidersFailedError: se nenhum provedor conseguir responder.
        """
        tokens = max_tokens or settings.ai_max_tokens
        last_error: Exception | None = None

        for provider in self._providers:
            if not provider.is_available():
                logger.info("Provedor %s indisponível — pulando.", provider.name)
                continue
            try:
                logger.info("Tentando provedor: %s", provider.name)
                response = await provider.generate(
                    messages, system=system, max_tokens=tokens
                )
                logger.info(
                    "Resposta de %s (%s) — tokens in/out: %d/%d",
                    response.provider,
                    response.model,
                    response.input_tokens,
                    response.output_tokens,
                )
                return response
            except AIProviderError as exc:
                # Registra o erro e segue para o próximo provedor (failover).
                last_error = exc
                logger.warning("Failover: %s falhou, tentando o próximo.", provider.name)

        raise AllProvidersFailedError(
            f"Todos os provedores de IA falharam. Último erro: {last_error}"
        )


# Instância única compartilhada por toda a aplicação.
ai_manager = AIManager()

```

### Arquivo: `backend/app/db/__init__.py`
```python
"""Camada de persistência (banco de dados).

Isola todo o acesso ao banco. A memória do agente vive aqui, de forma
CENTRALIZADA e INDEPENDENTE do modelo de IA — trocar Claude por GPT nunca
faz o agente perder histórico, contexto ou dados do cliente.
"""

```

### Arquivo: `backend/app/db/base.py`
```python
"""Infraestrutura do banco de dados (SQLAlchemy async).

Cria o `engine` (conexão), a fábrica de sessões e a função de inicialização
que cria as tabelas. O mesmo código atende SQLite e PostgreSQL — basta mudar
a `DATABASE_URL` no `.env`.
"""

from __future__ import annotations

import os

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """Classe base de todos os modelos ORM (tabelas)."""


# Engine assíncrono compartilhado por toda a aplicação.
engine = create_async_engine(settings.database_url, echo=False, future=True)

# Fábrica de sessões. `expire_on_commit=False` permite usar objetos após o
# commit sem consultas extras ao banco.
SessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


def _ensure_sqlite_dir() -> None:
    """Garante que a pasta do arquivo SQLite exista (ex.: ./storage)."""
    url = settings.database_url
    if "sqlite" in url and ":///" in url:
        path = url.split(":///", 1)[1].split("?", 1)[0]
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)


async def init_db() -> None:
    """Cria as tabelas no banco (idempotente — seguro rodar sempre)."""
    _ensure_sqlite_dir()
    # Importa os modelos para que sejam registrados no metadata antes do
    # create_all. O import fica aqui dentro para evitar import circular.
    from app.db import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Banco de dados inicializado (%s).", settings.database_url)

```

### Arquivo: `backend/app/db/models.py`
```python
"""Modelos ORM — as tabelas que guardam a memória do agente.

Modelagem baseada nas seções MEMÓRIA e ETAPAS DO CRM do documento do projeto:
  * Lead          → o cliente/potencial cliente e seus dados cadastrais.
  * Conversation  → um atendimento (thread de conversa) de um lead.
  * Message       → cada mensagem trocada (do cliente ou do agente).

A memória é INDEPENDENTE do modelo de IA: guardamos qual provedor/modelo
respondeu apenas como metadado, mas o histórico em si é neutro.
"""

from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _now() -> datetime:
    """Data/hora atual em UTC (timezone-aware)."""
    return datetime.now(timezone.utc)


class LeadStatus(str, enum.Enum):
    """Etapas do funil do CRM (conforme 'ETAPAS DO CRM' no documento)."""

    NOVO_LEAD = "novo_lead"
    PRIMEIRO_ATENDIMENTO = "primeiro_atendimento"
    ANALISE_JURIDICA = "analise_juridica"
    DOCUMENTACAO_PENDENTE = "documentacao_pendente"
    DOCUMENTACAO_RECEBIDA = "documentacao_recebida"
    CONTRATO_GERADO = "contrato_gerado"
    CONTRATO_ENVIADO = "contrato_enviado"
    CONTRATO_ASSINADO = "contrato_assinado"
    PAGAMENTO = "pagamento"
    PROCESSO_EM_ANDAMENTO = "processo_em_andamento"
    CLIENTE_FINALIZADO = "cliente_finalizado"
    ARQUIVADO = "arquivado"


class Lead(Base):
    """Cliente/lead e seus dados cadastrais (memória de longo prazo)."""

    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Identificação (o telefone do WhatsApp é a chave natural).
    phone: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    state: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Contexto do atendimento.
    problem: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[LeadStatus] = mapped_column(
        SAEnum(LeadStatus), default=LeadStatus.NOVO_LEAD, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_now, onupdate=_now
    )

    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="lead", cascade="all, delete-orphan"
    )


class Conversation(Base):
    """Um atendimento (thread) pertencente a um lead."""

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lead_id: Mapped[int] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    lead: Mapped[Lead] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(Base):
    """Uma mensagem individual da conversa (do cliente ou do agente)."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), index=True
    )

    # "user" (cliente) ou "assistant" (agente).
    role: Mapped[str] = mapped_column(String(32))
    content: Mapped[str] = mapped_column(Text)

    # Metadados de IA (controle de custos e auditoria). Neutros em relação
    # ao conteúdo — a memória continua independente do modelo.
    provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    conversation: Mapped[Conversation] = relationship(back_populates="messages")

```

### Arquivo: `backend/app/memory/__init__.py`
```python
"""Camada de Memória — une persistência (banco) e IA.

Responsável por: recuperar o histórico do cliente, montar o contexto para o
modelo, chamar a camada de IA e salvar a resposta. É aqui que se garante que
o agente "continue exatamente de onde a conversa parou", mesmo após meses.
"""

```

### Arquivo: `backend/app/memory/repository.py`
```python
"""Repositório de conversas — todo o acesso ao banco fica isolado aqui.

Padrão Repository: o serviço de memória não escreve SQL nem conhece o ORM;
ele apenas pede operações de alto nível (buscar lead, adicionar mensagem...).
Isso mantém baixo acoplamento e facilita testes.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Conversation, Lead, LeadStatus, Message


class ConversationRepository:
    """Operações de persistência sobre leads, conversas e mensagens."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_create_lead(
        self, phone: str, *, name: str | None = None
    ) -> Lead:
        """Busca o lead pelo telefone; cria um novo se ainda não existir."""
        result = await self.session.execute(
            select(Lead).where(Lead.phone == phone)
        )
        lead = result.scalar_one_or_none()
        if lead is None:
            lead = Lead(phone=phone, name=name, status=LeadStatus.NOVO_LEAD)
            self.session.add(lead)
            await self.session.flush()  # garante o lead.id preenchido
        return lead

    async def get_or_create_conversation(self, lead: Lead) -> Conversation:
        """Retorna a conversa mais recente do lead; cria uma se não houver."""
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.lead_id == lead.id)
            .order_by(Conversation.id.desc())
        )
        conversation = result.scalars().first()
        if conversation is None:
            conversation = Conversation(lead_id=lead.id)
            self.session.add(conversation)
            await self.session.flush()
        return conversation

    async def get_messages(self, conversation_id: int) -> list[Message]:
        """Retorna o histórico completo da conversa, em ordem cronológica."""
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.id)
        )
        return list(result.scalars().all())

    async def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        *,
        provider: str | None = None,
        model: str | None = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
    ) -> Message:
        """Adiciona uma mensagem à conversa e retorna o registro criado."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        self.session.add(message)
        await self.session.flush()
        return message

```

### Arquivo: `backend/app/memory/service.py`
```python
"""Serviço de Memória — orquestra o fluxo completo de um turno de conversa.

Fluxo de `handle_turn`:
  1. Identifica (ou cria) o lead pelo telefone.
  2. Recupera o histórico da conversa no banco.
  3. Persiste a mensagem do cliente.
  4. Chama a camada de IA com TODO o contexto (histórico + nova mensagem).
  5. Persiste a resposta do agente (com metadados de custo).
  6. Avança o status do lead no funil, quando aplicável.

Como o histórico vem do banco e é neutro, a troca de modelo de IA (failover)
nunca faz o agente "esquecer" a conversa.
"""

from __future__ import annotations

from app.ai.manager import AIManager, ai_manager
from app.ai.schemas import AIMessage, AIResponse, Role
from app.core.logging import get_logger
from app.db.base import SessionLocal
from app.db.models import LeadStatus
from app.memory.repository import ConversationRepository

logger = get_logger(__name__)


class MemoryService:
    """Une persistência e IA para produzir uma resposta com memória."""

    def __init__(self, *, session_factory=SessionLocal, manager: AIManager | None = None) -> None:
        # Injeção de dependência: em testes passamos uma fábrica de sessões e
        # um gerenciador falso; em produção usamos os padrões globais.
        self._session_factory = session_factory
        self._manager = manager or ai_manager

    async def handle_turn(
        self,
        phone: str,
        text: str,
        *,
        system: str | None = None,
        name: str | None = None,
    ) -> AIResponse:
        """Processa uma mensagem do cliente e devolve a resposta do agente."""
        async with self._session_factory() as session:
            repo = ConversationRepository(session)

            lead = await repo.get_or_create_lead(phone, name=name)
            conversation = await repo.get_or_create_conversation(lead)

            # 1) Monta o contexto: histórico salvo + a nova mensagem do cliente.
            history = await repo.get_messages(conversation.id)
            ai_messages: list[AIMessage] = [
                AIMessage(role=Role(m.role), content=m.content) for m in history
            ]
            ai_messages.append(AIMessage(role=Role.USER, content=text))

            # 2) Persiste a mensagem do cliente e confirma (memória preservada
            #    mesmo se a IA falhar depois).
            await repo.add_message(conversation.id, Role.USER.value, text)
            await session.commit()

            # 3) Chama a IA (pode acionar failover internamente).
            response = await self._manager.generate(ai_messages, system=system)

            # 4) Persiste a resposta do agente com metadados de custo.
            await repo.add_message(
                conversation.id,
                Role.ASSISTANT.value,
                response.content,
                provider=response.provider,
                model=response.model,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
            )

            # 5) Avança o status do funil no primeiro atendimento respondido.
            if lead.status == LeadStatus.NOVO_LEAD:
                lead.status = LeadStatus.PRIMEIRO_ATENDIMENTO

            await session.commit()
            return response


# Instância única compartilhada pela aplicação.
memory_service = MemoryService()

```

### Arquivo: `backend/app/main.py`
```python
"""Ponto de entrada da aplicação (FastAPI).

Expõe a API HTTP. Nesta etapa temos:
  * GET  /                 → status da aplicação (healthcheck).
  * GET  /initial-message  → mensagem inicial obrigatória do atendimento.
  * POST /chat             → conversa COM MEMÓRIA (histórico persistido).

O banco de dados é inicializado automaticamente no startup (lifespan).

Executar em desenvolvimento:
    uvicorn app.main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.exceptions import AllProvidersFailedError
from app.core.logging import get_logger, setup_logging
from app.db.base import init_db
from app.memory.service import memory_service

# Configura os logs assim que o módulo é carregado.
setup_logging()
logger = get_logger(__name__)

# Personalidade + regras do agente (instrução de sistema).
SYSTEM_PROMPT = (
    "Você é a MARQUES IA, assistente virtual do escritório Marques Advogados "
    "Associados, especializado em Direito Bancário, Ações Revisionais, Busca e "
    "Apreensão de Veículos e Renegociação de Dívidas. Seja educada, humana, "
    "objetiva e persuasiva. Nunca revele que é uma inteligência artificial. "
    "Adapte a linguagem ao perfil do cliente."
)

# Mensagem inicial obrigatória (definida no documento do projeto).
INITIAL_MESSAGE = (
    "Olá! Seja muito bem-vindo(a) à Marques Advogados Associados. "
    "Meu nome é MARQUES IA. Sou a assistente virtual do escritório e estou "
    "aqui para ajudá-lo da melhor forma possível. Nosso atendimento é "
    "especializado em Direito Bancário, Ações Revisionais, Busca e Apreensão "
    "de Veículos e Renegociação de Dívidas. Conte, por favor, o que aconteceu "
    "para que eu possa entender seu caso e direcionar você da forma mais "
    "rápida possível."
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida da aplicação: cria as tabelas do banco no startup."""
    await init_db()
    logger.info("Aplicação iniciada: %s", settings.app_name)
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)


class ChatRequest(BaseModel):
    """Corpo da requisição do endpoint /chat."""

    phone: str = Field(..., description="Telefone do cliente (chave de memória).")
    message: str = Field(..., description="Mensagem enviada pelo cliente.")
    name: str | None = Field(default=None, description="Nome do cliente (opcional).")


class ChatResponse(BaseModel):
    """Corpo da resposta do endpoint /chat."""

    reply: str
    provider: str
    model: str


@app.get("/")
async def health() -> dict:
    """Healthcheck simples — confirma que a aplicação está no ar."""
    return {"app": settings.app_name, "env": settings.app_env, "status": "ok"}


@app.get("/initial-message")
async def initial_message() -> dict:
    """Retorna a mensagem inicial obrigatória do atendimento."""
    return {"message": INITIAL_MESSAGE}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Recebe uma mensagem do cliente e devolve a resposta do agente.

    Toda a conversa é persistida: o agente lembra do histórico do cliente
    (identificado pelo telefone) e continua de onde parou. O failover entre
    modelos é transparente e não afeta a memória.
    """
    try:
        response = await memory_service.handle_turn(
            request.phone,
            request.message,
            system=SYSTEM_PROMPT,
            name=request.name,
        )
    except AllProvidersFailedError:
        logger.error("Nenhum provedor de IA respondeu à mensagem do cliente.")
        # Resposta de fallback amigável — o cliente nunca vê um erro técnico.
        return ChatResponse(
            reply=(
                "Estou finalizando alguns detalhes do seu atendimento e já "
                "retorno. Pode me contar um pouco mais sobre o seu caso?"
            ),
            provider="fallback",
            model="none",
        )

    return ChatResponse(
        reply=response.content,
        provider=response.provider,
        model=response.model,
    )

```

### Arquivo: `backend/tests/__init__.py`
```python
"""Pacote de testes automatizados."""

```

### Arquivo: `backend/tests/test_ai_manager.py`
```python
"""Testes da camada de IA — foco no comportamento de FAILOVER.

Usamos provedores "falsos" (fakes) para testar a lógica do gerenciador SEM
gastar tokens nem depender de rede. Isso comprova que a abstração funciona:
o gerenciador não sabe (nem precisa saber) qual modelo real está por trás.
"""

from __future__ import annotations

import pytest

from app.ai.base import AIProvider
from app.ai.manager import AIManager
from app.ai.schemas import AIMessage, AIResponse, Role
from app.core.exceptions import AIProviderError, AllProvidersFailedError


class _FakeOkProvider(AIProvider):
    """Provedor falso que sempre responde com sucesso."""

    name = "fake_ok"

    async def generate(self, messages, *, system=None, max_tokens=1024) -> AIResponse:
        return AIResponse(content="ok", provider=self.name, model="fake-1")

    def is_available(self) -> bool:
        return True


class _FakeFailProvider(AIProvider):
    """Provedor falso que sempre falha (simula indisponibilidade)."""

    name = "fake_fail"

    async def generate(self, messages, *, system=None, max_tokens=1024) -> AIResponse:
        raise AIProviderError("simulação de falha")

    def is_available(self) -> bool:
        return True


def _manager_with(providers: list[AIProvider]) -> AIManager:
    """Cria um AIManager e injeta provedores de teste."""
    manager = AIManager()
    manager._providers = providers  # noqa: SLF001 (injeção só para teste)
    return manager


@pytest.mark.asyncio
async def test_usa_primeiro_provedor_quando_ok() -> None:
    manager = _manager_with([_FakeOkProvider(), _FakeFailProvider()])
    resp = await manager.generate([AIMessage(role=Role.USER, content="oi")])
    assert resp.provider == "fake_ok"


@pytest.mark.asyncio
async def test_failover_quando_primeiro_falha() -> None:
    # O primeiro falha, então o gerenciador deve alternar para o segundo.
    manager = _manager_with([_FakeFailProvider(), _FakeOkProvider()])
    resp = await manager.generate([AIMessage(role=Role.USER, content="oi")])
    assert resp.provider == "fake_ok"


@pytest.mark.asyncio
async def test_erro_quando_todos_falham() -> None:
    manager = _manager_with([_FakeFailProvider(), _FakeFailProvider()])
    with pytest.raises(AllProvidersFailedError):
        await manager.generate([AIMessage(role=Role.USER, content="oi")])

```

### Arquivo: `backend/tests/test_memory.py`
```python
"""Testes da camada de memória.

Comprovam que o histórico é persistido e reaproveitado entre turnos, SEM
gastar tokens (usamos um gerenciador de IA falso) e usando um banco SQLite
temporário e isolado por teste.
"""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.ai.schemas import AIMessage, AIResponse
from app.db.base import Base
from app.db.models import LeadStatus
from app.memory.repository import ConversationRepository
from app.memory.service import MemoryService


class _FakeManager:
    """Gerenciador de IA falso: registra o contexto recebido e responde fixo."""

    def __init__(self) -> None:
        self.last_messages: list[AIMessage] | None = None

    async def generate(self, messages, *, system=None, max_tokens=None) -> AIResponse:
        self.last_messages = messages
        return AIResponse(
            content="resposta do agente",
            provider="fake",
            model="fake-1",
            input_tokens=10,
            output_tokens=5,
        )


@pytest.fixture
async def session_factory(tmp_path):
    """Cria um banco SQLite temporário com as tabelas já criadas."""
    url = f"sqlite+aiosqlite:///{tmp_path}/test.db"
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


async def test_memoria_persiste_e_cresce(session_factory) -> None:
    fake = _FakeManager()
    service = MemoryService(session_factory=session_factory, manager=fake)

    # 1º turno: o contexto enviado à IA tem apenas a mensagem atual.
    await service.handle_turn("5511999999999", "Meu carro foi apreendido")
    assert fake.last_messages is not None
    assert len(fake.last_messages) == 1

    # 2º turno: agora o contexto inclui user1 + assistant1 + user2 = 3.
    await service.handle_turn("5511999999999", "E agora, o que faço?")
    assert len(fake.last_messages) == 3

    # No banco: 2 mensagens do cliente + 2 do agente = 4.
    async with session_factory() as session:
        repo = ConversationRepository(session)
        lead = await repo.get_or_create_lead("5511999999999")
        conversation = await repo.get_or_create_conversation(lead)
        messages = await repo.get_messages(conversation.id)

    assert len(messages) == 4
    # O status do lead avançou no funil após o primeiro atendimento.
    assert lead.status == LeadStatus.PRIMEIRO_ATENDIMENTO


async def test_leads_diferentes_nao_compartilham_memoria(session_factory) -> None:
    fake = _FakeManager()
    service = MemoryService(session_factory=session_factory, manager=fake)

    await service.handle_turn("5511111111111", "Olá")
    await service.handle_turn("5522222222222", "Oi")

    # O segundo cliente é novo: seu contexto tem só a própria mensagem.
    assert len(fake.last_messages) == 1

```

---

## 4. Como preparar o ambiente e rodar (passo a passo)

Todos os comandos são executados **dentro da pasta `backend/`**.

**Passo 1 — Criar o ambiente virtual** (isola as dependências do projeto):

```bash
python3 -m venv .venv
```

**Passo 2 — Ativar o ambiente virtual:**

```bash
# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

**Passo 3 — Instalar as dependências:**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Passo 4 — Criar o arquivo de configuração a partir do modelo:**

```bash
cp .env.example .env
```

**Passo 5 — Editar o `.env` e colocar sua chave da Anthropic:**

```
ANTHROPIC_API_KEY="sk-ant-sua-chave-real-aqui"
```

**Passo 6 — Rodar os testes** (confirma que tudo funciona, sem gastar tokens):

```bash
pytest
```

Você deve ver `5 passed`.

**Passo 7 — Subir a aplicação:**

```bash
uvicorn app.main:app --reload
```

> Dica: no Windows/macOS, se preferir, os passos 1 a 4 podem ser feitos de uma
> só vez com `bash setup.sh`.

---

## 5. O que fazer depois de tudo pronto (testar)

Com a aplicação rodando em `http://127.0.0.1:8000`:

**1) Abra a documentação interativa** (gerada automaticamente):

```
http://127.0.0.1:8000/docs
```

Por ali você consegue testar todos os endpoints pelo navegador, sem comandos.

**2) Healthcheck** (confirma que está no ar):

```bash
curl http://127.0.0.1:8000/
```

**3) Mensagem inicial obrigatória do atendimento:**

```bash
curl http://127.0.0.1:8000/initial-message
```

**4) Conversar com o agente** (o `phone` identifica o cliente e ativa a memória):

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"phone": "5511987654321", "message": "Meu carro foi apreendido, o que faço?"}'
```

**5) Testar a memória:** envie uma segunda mensagem com o **mesmo `phone`**.
O agente vai lembrar do que você disse antes e continuar de onde parou:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"phone": "5511987654321", "message": "E quanto tempo demora o processo?"}'
```

---

## 6. Como funciona (resumo da arquitetura)

- **Failover automático:** o `AIManager` tenta o Claude primeiro. Se falhar,
  alterna para o GPT sem o cliente perceber. Se todos falharem, responde com
  uma mensagem amigável (nunca um erro técnico).
- **Memória independente do modelo:** o histórico fica no banco. Trocar de
  modelo de IA nunca faz o agente esquecer a conversa.
- **Preparado para PostgreSQL:** trocar SQLite por PostgreSQL é só mudar a
  `DATABASE_URL` no `.env` (sem tocar no código).

---

## 7. Como adicionar um novo modelo de IA (ex.: Gemini)

Graças à camada de abstração, você **não altera** o CRM, a memória nem o
`main.py`. Basta:

1. Criar `app/ai/providers/gemini_provider.py` implementando `AIProvider`.
2. Registrá-lo no dicionário `_PROVIDER_REGISTRY` em `app/ai/manager.py`.
3. Adicionar `gemini` ao `AI_PROVIDER_ORDER` no `.env`.

---

## 8. Solução de problemas (erros comuns)

| Sintoma | Causa provável | Solução |
|---|---|---|
| `command not found: python3` | Python não instalado | Instale o Python 3.11+ |
| `ModuleNotFoundError` | Ambiente virtual não ativado | Rode `source .venv/bin/activate` |
| `/chat` responde com `provider: fallback` | `ANTHROPIC_API_KEY` vazia/errada no `.env` | Coloque uma chave válida e reinicie |
| Porta 8000 ocupada | Outro processo usando a porta | Use `uvicorn app.main:app --reload --port 8001` |

---

## 9. Próximas etapas do projeto

- [ ] Webhook do WhatsApp Business + QR Code de conexão.
- [ ] CRM completo (funil visual, contratos, documentos).
- [ ] Geração automática de contratos em PDF.
- [ ] Painel administrativo e controle de custos por tokens.
- [ ] Migrações de banco com Alembic.
- [ ] Segurança (JWT, LGPD, rate limit).
