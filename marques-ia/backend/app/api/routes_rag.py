# -*- coding: utf-8 -*-
"""
Endpoints da base de conhecimento jurídica (RAG): cadastro de trechos de
referência e busca por relevância, usada internamente pelo agente e também
exposta para consulta manual pelo painel administrativo.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.audit import registrar_log
from app.database.session import get_db
from app.models.case import AREAS_JURIDICAS
from app.models.knowledge import BaseConhecimento
from app.models.user import AdminUser
from app.rag.service import buscar_contexto
from app.schemas.knowledge import ConhecimentoCreate, ConhecimentoOut, TrechoRelevante

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/documentos", response_model=ConhecimentoOut, status_code=status.HTTP_201_CREATED)
def adicionar_conhecimento(
    payload: ConhecimentoCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    if payload.area_juridica not in AREAS_JURIDICAS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"area_juridica deve ser uma de: {AREAS_JURIDICAS}",
        )

    doc = BaseConhecimento(
        area_juridica=payload.area_juridica,
        titulo=payload.titulo,
        conteudo=payload.conteudo,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    registrar_log(db, acao="adicionar_conhecimento", entidade="base_conhecimento",
                  entidade_id=doc.id, usuario_email=admin.email)
    return doc


@router.get("/documentos", response_model=list[ConhecimentoOut])
def listar_conhecimento(
    area_juridica: Optional[str] = None,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    query = db.query(BaseConhecimento)
    if area_juridica:
        query = query.filter(BaseConhecimento.area_juridica == area_juridica)
    return query.order_by(BaseConhecimento.criado_em.desc()).all()


@router.delete("/documentos/{documento_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_conhecimento(
    documento_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    doc = db.query(BaseConhecimento).filter(BaseConhecimento.id == documento_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")
    db.delete(doc)
    db.commit()
    registrar_log(db, acao="remover_conhecimento", entidade="base_conhecimento",
                  entidade_id=documento_id, usuario_email=admin.email)
    return None


@router.get("/buscar", response_model=list[TrechoRelevante])
def buscar(
    q: str = Query(..., min_length=2, description="Consulta em linguagem natural"),
    area_juridica: Optional[str] = None,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Testa manualmente a busca de relevância usada internamente pelo agente."""
    return buscar_contexto(db, consulta=q, area_juridica=area_juridica)
