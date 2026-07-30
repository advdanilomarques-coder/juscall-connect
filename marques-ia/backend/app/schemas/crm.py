# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ---------------- Cliente ----------------

class ClienteOut(BaseModel):
    id: int
    telefone: str
    nome: Optional[str]
    email: Optional[str]
    criado_em: datetime
    ultimo_contato_em: datetime

    class Config:
        from_attributes = True


class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None


# ---------------- Caso ----------------

class CasoCreate(BaseModel):
    cliente_id: int
    area_juridica: str = Field(default="outro")
    resumo: Optional[str] = None
    responsavel: Optional[str] = None


class CasoUpdate(BaseModel):
    area_juridica: Optional[str] = None
    etapa_funil: Optional[str] = None
    status: Optional[str] = None
    responsavel: Optional[str] = None
    resumo: Optional[str] = None


class CasoOut(BaseModel):
    id: int
    cliente_id: int
    area_juridica: str
    etapa_funil: str
    status: str
    responsavel: Optional[str]
    resumo: Optional[str]
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True


class KanbanColuna(BaseModel):
    etapa: str
    casos: list[CasoOut]
