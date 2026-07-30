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
        case_sensitive=False,
    )

    # --- Identificação da aplicação ---
    app_name: str = "Marques IA"
    app_env: str = "development"
    debug: bool = True

    # --- Dados do escritório (usados nos contratos e nas mensagens) ---
    firm_name: str = "Marques Advogados Associados"
    firm_lawyer: str = "Dr. Marques"
    firm_oab: str = "OAB/XX 000000"
    firm_city: str = "São Paulo/SP"

    # --- Chaves das APIs de IA (Camada AI Provider) ---
    gemini_api_key: str = ""
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    deepseek_api_key: str = ""
    mistral_api_key: str = ""
    openrouter_api_key: str = ""
    grok_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"

    # --- Seleção e ordem de failover dos provedores de IA ---
    ai_provider_order: str = "claude,gemini,openai"

    # --- Modelos específicos por provedor ---
    gemini_model: str = "gemini-2.0-flash"
    claude_model: str = "claude-opus-4-8"
    openai_model: str = "gpt-4o"
    deepseek_model: str = "deepseek-chat"
    mistral_model: str = "mistral-large-latest"
    openrouter_model: str = "anthropic/claude-3.5-sonnet"
    grok_model: str = "grok-2-latest"
    ollama_model: str = "llama3.1"

    # --- Roteamento inteligente por tipo de tarefa ---
    # Ex.: "atendimento:claude,analise_juridica:openai,resumo:gemini"
    ai_task_routing: str = ""

    # --- Parâmetros de geração e resiliência ---
    ai_max_tokens: int = 1024
    ai_max_retries: int = 2
    ai_retry_backoff: float = 0.5

    # --- Banco de dados (memória persistente + CRM) ---
    database_url: str = "sqlite+aiosqlite:///./storage/marques_ia.db"

    # --- Segurança / painel administrativo ---
    jwt_secret: str = "troque-esta-chave-em-producao"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 720
    admin_email: str = "admin@marquesadvogados.com.br"
    admin_password: str = "troque-esta-senha"
    rate_limit_per_minute: int = 60

    # --- WhatsApp Business API ---
    whatsapp_verify_token: str = "token-de-verificacao-do-webhook"
    whatsapp_access_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_api_base: str = "https://graph.facebook.com/v21.0"

    # --- Armazenamento de documentos ---
    storage_dir: str = "./storage/documents"

    # --- Logs ---
    log_level: str = "INFO"

    @property
    def provider_order(self) -> list[str]:
        """Converte "claude,gemini" em ["claude", "gemini"] já normalizado."""
        return [
            p.strip().lower()
            for p in self.ai_provider_order.split(",")
            if p.strip()
        ]

    @property
    def task_routing(self) -> dict[str, str]:
        """Converte "atendimento:claude,resumo:gemini" em um dicionário.

        Retorna {tarefa: provedor}. Tarefas sem regra caem na ordem padrão.
        """
        routing: dict[str, str] = {}
        for pair in self.ai_task_routing.split(","):
            pair = pair.strip()
            if not pair or ":" not in pair:
                continue
            task, provider = pair.split(":", 1)
            routing[task.strip().lower()] = provider.strip().lower()
        return routing


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
