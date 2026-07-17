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
    gemini_api_key: str = ""

    # --- Seleção e ordem de failover dos provedores de IA ---
    # Ex.: "claude,openai" — o primeiro é o principal; os demais são reserva.
    # Para usar a opção GRATUITA, defina: AI_PROVIDER_ORDER="gemini"
    ai_provider_order: str = "claude,gemini,openai"
    claude_model: str = "claude-opus-4-8"
    openai_model: str = "gpt-4o"
    gemini_model: str = "gemini-2.5-flash"
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
