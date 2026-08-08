"""Application configuration via Pydantic settings (12-factor / .env)."""
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    app_name: str = "PedroIA Backend"
    environment: str = "development"
    debug: bool = True
    api_prefix: str = "/api/v1"
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])

    # --- Auth ---
    # Comma-separated list of accepted API keys. Empty = auth disabled (local mode).
    api_keys: str = ""
    # When true, the app refuses to start in production without api_keys set
    # (prevents an open, billable public backend by accident).
    require_auth_in_production: bool = True

    # --- User accounts / JWT (for the website login) ---
    jwt_secret: str = "change-me-in-production"
    jwt_expire_minutes: int = 10080  # 7 days
    allow_signup: bool = True

    # --- Rate limiting (protects a hosted backend from runaway costs) ---
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 30   # requests per client per minute
    rate_limit_per_day: int = 1000    # requests per client per day

    # --- Database / cache ---
    database_url: str = "sqlite+aiosqlite:///./pedroia.db"
    redis_url: str = "redis://localhost:6379/0"

    # --- LLM: cloud providers (all optional) ---
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-latest"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    # Groq — generous free tier, no billing required (OpenAI-compatible API).
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # --- LLM: local (Ollama) ---
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    ollama_completion_model: str = "qwen2.5-coder:1.5b"

    # Priority order for cloud providers when mode=auto/cloud.
    cloud_priority: List[str] = Field(default_factory=lambda: ["anthropic", "openai", "groq", "gemini", "deepseek"])

    @property
    def allowed_api_keys(self) -> List[str]:
        return [k.strip() for k in self.api_keys.split(",") if k.strip()]

    @property
    def auth_enabled(self) -> bool:
        return len(self.allowed_api_keys) > 0


@lru_cache
def get_settings() -> Settings:
    return Settings()
