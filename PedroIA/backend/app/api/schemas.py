"""Pydantic request/response models for the public API.

Input bounds are intentional (defense in depth): they cap request size so a
single call can't exhaust memory, tokens or the provider's context window.
"""
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

# Generous limits — "muitos caracteres" — but bounded.
MAX_MESSAGE_CHARS = 100_000       # per message
MAX_TOTAL_CHARS = 400_000         # whole conversation
MAX_MESSAGES = 200


class ProjectContext(BaseModel):
    file_path: Optional[str] = Field(default=None, max_length=1000)
    language: Optional[str] = Field(default=None, max_length=60)
    selection: Optional[str] = Field(default=None, max_length=MAX_MESSAGE_CHARS)
    diagnostics: Optional[List[str]] = None
    open_files: Optional[List[str]] = None
    workspace_name: Optional[str] = Field(default=None, max_length=300)


class ChatMessageIn(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(..., max_length=MAX_MESSAGE_CHARS)


class ChatRequest(BaseModel):
    messages: List[ChatMessageIn] = Field(..., min_length=1, max_length=MAX_MESSAGES)
    mode: Literal["auto", "cloud", "local"] = "auto"
    context: Optional[ProjectContext] = None
    session_id: Optional[str] = Field(default=None, max_length=128)
    max_tokens: int = Field(default=2048, ge=16, le=8000)

    @field_validator("messages")
    @classmethod
    def _total_size(cls, v: List[ChatMessageIn]) -> List[ChatMessageIn]:
        total = sum(len(m.content) for m in v)
        if total > MAX_TOTAL_CHARS:
            raise ValueError(
                f"Conversa muito longa ({total} caracteres). Limite: {MAX_TOTAL_CHARS}. "
                "Comece um novo chat ou resuma o contexto."
            )
        return v


class ChatResponse(BaseModel):
    content: str
    model: str
    provider: str
    mode: str


class CompletionRequest(BaseModel):
    prefix: str = Field(default="", max_length=20_000)
    suffix: str = Field(default="", max_length=20_000)
    language: str = Field(default="plaintext", max_length=60)
    file_path: Optional[str] = Field(default=None, max_length=1000)
    mode: Literal["auto", "cloud", "local"] = "auto"
    max_tokens: int = Field(default=96, ge=8, le=512)


class CompletionResponse(BaseModel):
    completion: str
    model: str


class HealthResponse(BaseModel):
    status: str
    online: bool
    cloud_providers: List[str]
    ollama: bool
