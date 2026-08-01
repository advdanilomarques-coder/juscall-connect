# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    papel: str = "admin"
    nome: Optional[str] = None


class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str
    papel: str = "funcionario"  # 'admin' ou 'funcionario'


class UsuarioOut(BaseModel):
    id: int
    nome: str
    email: str
    papel: str
    ativo: bool

    class Config:
        from_attributes = True
