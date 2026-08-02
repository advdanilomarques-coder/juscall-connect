"""Pydantic request/response models for the public API."""
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ProjectContext(BaseModel):
    file_path: Optional[str] = None
    language: Optional[str] = None
    selection: Optional[str] = None
    diagnostics: Optional[List[str]] = None
    open_files: Optional[List[str]] = None
    workspace_name: Optional[str] = None


class ChatMessageIn(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessageIn] = Field(..., min_length=1)
    mode: Literal["auto", "cloud", "local"] = "auto"
    context: Optional[ProjectContext] = None
    session_id: Optional[str] = None
    max_tokens: int = 1024


class ChatResponse(BaseModel):
    content: str
    model: str
    provider: str
    mode: str


class CompletionRequest(BaseModel):
    prefix: str
    suffix: str = ""
    language: str = "plaintext"
    file_path: Optional[str] = None
    mode: Literal["auto", "cloud", "local"] = "auto"
    max_tokens: int = 128


class CompletionResponse(BaseModel):
    completion: str
    model: str


class HealthResponse(BaseModel):
    status: str
    online: bool
    cloud_providers: List[str]
    ollama: bool
