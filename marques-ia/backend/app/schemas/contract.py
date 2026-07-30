# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ContratoGerarRequest(BaseModel):
    caso_id: int
    tipo: str = Field(..., description="Ex.: 'acao_revisional', 'honorarios', 'busca_e_apreensao'")


class ContratoOut(BaseModel):
    id: int
    caso_id: int
    tipo: str
    status: str
    numero: Optional[str]
    gerado_em: datetime

    class Config:
        from_attributes = True


class ContratoEnviarResponse(BaseModel):
    enviado: bool
    destino: str
    contrato: ContratoOut
    detalhe: str
