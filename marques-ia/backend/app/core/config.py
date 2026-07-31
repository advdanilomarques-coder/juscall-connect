# -*- coding: utf-8 -*-
"""
Configurações centrais da aplicação Marques IA.

Toda a configuração vem de UM ÚNICO arquivo .env (ver .env.example na raiz
do projeto). Não deve existir nenhuma outra fonte de configuração.
"""
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ---- Aplicação ----
    APP_NAME: str = "Marques IA"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ---- Banco de dados ----
    DATABASE_URL: str
    POSTGRES_USER: str = "marques_ia"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "marques_ia"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # ---- Redis ----
    REDIS_URL: str = "redis://localhost:6379/0"

    # ---- IA — uma única chave de API (OpenRouter) ----
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL_PRIMARY: str = "meta-llama/llama-3.2-3b-instruct:free"
    OPENROUTER_MODEL_FALLBACK_1: str = "qwen/qwen-2.5-7b-instruct:free"
    OPENROUTER_MODEL_FALLBACK_2: str = "mistralai/mistral-7b-instruct:free"

    # ---- WhatsApp Business Cloud API ----
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER: str = "5511991537423"
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = ""
    WHATSAPP_BUSINESS_ACCOUNT_ID: str = ""
    WHATSAPP_APP_SECRET: str = ""

    # ---- E-mail (SMTP) — envio automático de contratos/notificações ao cliente ----
    # Se SMTP_HOST ficar em branco, o envio de e-mail fica DESATIVADO (o sistema
    # continua funcionando normalmente, apenas não dispara e-mails).
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""            # remetente; se vazio, usa SMTP_USER
    SMTP_FROM_NAME: str = "Marques Advogados Associados"
    SMTP_USE_TLS: bool = True           # STARTTLS (porta 587). Use False + SMTP_USE_SSL p/ porta 465.
    SMTP_USE_SSL: bool = False

    # ---- Transcrição de áudio (voz do WhatsApp) — OPCIONAL ----
    # Converte áudios de voz recebidos no WhatsApp em texto (Whisper), para o
    # agente entender e responder. Se TRANSCRICAO_API_KEY ficar em branco, o
    # recurso fica DESATIVADO e áudios recebem uma resposta pedindo texto.
    # Padrão: Groq (tem plano gratuito e é compatível com a API da OpenAI).
    # Pegue a chave grátis em https://console.groq.com/keys
    TRANSCRICAO_API_KEY: str = ""
    TRANSCRICAO_BASE_URL: str = "https://api.groq.com/openai/v1"
    TRANSCRICAO_MODELO: str = "whisper-large-v3-turbo"

    # ---- Administrador padrão (criado na primeira execução) ----
    ADMIN_DEFAULT_EMAIL: str = "admin@marquesadvogados.com.br"
    ADMIN_DEFAULT_PASSWORD: str = "troque_esta_senha_admin"
    ADMIN_DEFAULT_NAME: str = "Administrador"

    @property
    def OPENROUTER_MODELS_ORDER(self) -> List[str]:
        """Lista ordenada de modelos gratuitos a tentar, usando a mesma chave de API."""
        return [
            m for m in [
                self.OPENROUTER_MODEL_PRIMARY,
                self.OPENROUTER_MODEL_FALLBACK_1,
                self.OPENROUTER_MODEL_FALLBACK_2,
            ] if m
        ]

    @property
    def EMAIL_HABILITADO(self) -> bool:
        """True somente quando o SMTP está configurado o suficiente para enviar."""
        return bool(self.SMTP_HOST and (self.SMTP_FROM_EMAIL or self.SMTP_USER))

    @property
    def TRANSCRICAO_HABILITADA(self) -> bool:
        """True quando há chave configurada para transcrever áudio de voz."""
        return bool(self.TRANSCRICAO_API_KEY)


settings = Settings()
