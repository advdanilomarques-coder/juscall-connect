# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import BaseModel, Field


class ConhecimentoCreate(BaseModel):
    area_juridica: str = Field(..., description="Ex.: direito_bancario, acao_revisional, outro")
    titulo: str
    conteudo: str


class ConhecimentoOut(BaseModel):
    id: int
    area_juridica: str
    titulo: str
    conteudo: str
    criado_em: datetime

    class Config:
        from_attributes = True


class TrechoRelevante(BaseModel):
    titulo: str
    conteudo: str
    relevancia: float
