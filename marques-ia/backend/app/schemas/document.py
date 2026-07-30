# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DocumentoUploadResponse(BaseModel):
    id: int
    nome_arquivo: str
    texto_extraido_preview: str
    confianca_ocr: float
    revisao_manual_recomendada: bool


class DocumentoOut(BaseModel):
    id: int
    caso_id: int
    nome_arquivo: str
    tipo: str
    texto_ocr: Optional[str]
    confianca_ocr: Optional[float]
    upload_em: datetime

    class Config:
        from_attributes = True
