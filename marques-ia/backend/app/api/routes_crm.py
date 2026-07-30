# -*- coding: utf-8 -*-
"""
Endpoints do CRM: gestão de clientes, casos, visão kanban, auditoria e
direitos LGPD (exportação e exclusão de dados). Todos protegidos por
autenticação (usuário do painel administrativo).
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.audit import registrar_log
from app.database.session import get_db
from app.models.audit_log import LogAuditoria
from app.models.case import AREAS_JURIDICAS, ETAPAS_FUNIL, Caso
from app.models.client import Cliente
from app.models.contract import Contrato
from app.models.message import Mensagem
from app.models.user import AdminUser
from app.schemas.crm import (
    CasoCreate,
    CasoOut,
    CasoUpdate,
    ClienteOut,
    ClienteUpdate,
    KanbanColuna,
)

router = APIRouter(prefix="/crm", tags=["crm"])


# ==================== CLIENTES ====================

@router.get("/clientes", response_model=list[ClienteOut])
def listar_clientes(
    busca: Optional[str] = Query(default=None, description="Busca por nome ou telefone"),
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    query = db.query(Cliente)
    if busca:
        termo = f"%{busca}%"
        query = query.filter((Cliente.nome.ilike(termo)) | (Cliente.telefone.ilike(termo)))
    return query.order_by(Cliente.ultimo_contato_em.desc()).all()


@router.get("/clientes/{cliente_id}", response_model=ClienteOut)
def obter_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    return cliente


@router.patch("/clientes/{cliente_id}", response_model=ClienteOut)
def atualizar_cliente(
    cliente_id: int,
    payload: ClienteUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")

    if payload.nome is not None:
        cliente.nome = payload.nome

    if payload.email is not None:
        email = payload.email.strip()
        if email and ("@" not in email or "." not in email.split("@")[-1]):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="E-mail inválido.",
            )
        cliente.email = email or None

    db.commit()
    db.refresh(cliente)
    registrar_log(db, acao="atualizar", entidade="cliente", entidade_id=cliente.id, usuario_email=admin.email)
    return cliente


# -------- LGPD: exportação e exclusão de dados do cliente --------

@router.get("/clientes/{cliente_id}/exportar")
def exportar_dados_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """Exporta todos os dados pessoais de um cliente (direito de acesso — LGPD art. 18)."""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")

    casos = db.query(Caso).filter(Caso.cliente_id == cliente_id).all()
    mensagens = (
        db.query(Mensagem)
        .filter(Mensagem.cliente_id == cliente_id)
        .order_by(Mensagem.criado_em)
        .all()
    )

    dados = {
        "cliente": {
            "id": cliente.id,
            "telefone": cliente.telefone,
            "nome": cliente.nome,
            "email": cliente.email,
            "criado_em": cliente.criado_em.isoformat(),
            "ultimo_contato_em": cliente.ultimo_contato_em.isoformat(),
        },
        "casos": [
            {
                "id": c.id, "area_juridica": c.area_juridica, "etapa_funil": c.etapa_funil,
                "status": c.status, "resumo": c.resumo, "criado_em": c.criado_em.isoformat(),
            }
            for c in casos
        ],
        "mensagens": [
            {"role": m.role, "conteudo": m.conteudo, "criado_em": m.criado_em.isoformat()}
            for m in mensagens
        ],
    }

    registrar_log(
        db, acao="exportar_dados_lgpd", entidade="cliente",
        entidade_id=cliente_id, usuario_email=admin.email,
    )
    return dados


@router.delete("/clientes/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def apagar_dados_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """Apaga todos os dados de um cliente (direito de exclusão — LGPD art. 18, inciso VI)."""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")

    casos_ids = [c.id for c in db.query(Caso.id).filter(Caso.cliente_id == cliente_id).all()]

    db.query(Mensagem).filter(Mensagem.cliente_id == cliente_id).delete(synchronize_session=False)
    if casos_ids:
        db.query(Contrato).filter(Contrato.caso_id.in_(casos_ids)).delete(synchronize_session=False)
        db.query(Caso).filter(Caso.cliente_id == cliente_id).delete(synchronize_session=False)

    db.delete(cliente)

    # Registra a auditoria ANTES de excluir de vez, guardando o telefone nos detalhes
    # (o registro do cliente não existirá mais para consulta posterior).
    registrar_log(
        db, acao="apagar_dados_lgpd", entidade="cliente",
        entidade_id=cliente_id, usuario_email=admin.email, detalhes=f"telefone={cliente.telefone}",
    )
    db.commit()
    return None


# ==================== CASOS ====================

@router.post("/casos", response_model=CasoOut, status_code=status.HTTP_201_CREATED)
def criar_caso(
    payload: CasoCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    cliente = db.query(Cliente).filter(Cliente.id == payload.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")

    if payload.area_juridica not in AREAS_JURIDICAS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"area_juridica deve ser uma de: {AREAS_JURIDICAS}",
        )

    caso = Caso(
        cliente_id=payload.cliente_id,
        area_juridica=payload.area_juridica,
        resumo=payload.resumo,
        responsavel=payload.responsavel,
        etapa_funil="novo_lead",
        status="aberto",
    )
    db.add(caso)
    db.commit()
    db.refresh(caso)
    registrar_log(db, acao="criar", entidade="caso", entidade_id=caso.id, usuario_email=admin.email)
    return caso


@router.get("/casos", response_model=list[CasoOut])
def listar_casos(
    etapa_funil: Optional[str] = None,
    area_juridica: Optional[str] = None,
    status_filtro: Optional[str] = Query(default=None, alias="status"),
    cliente_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    query = db.query(Caso)
    if etapa_funil:
        query = query.filter(Caso.etapa_funil == etapa_funil)
    if area_juridica:
        query = query.filter(Caso.area_juridica == area_juridica)
    if status_filtro:
        query = query.filter(Caso.status == status_filtro)
    if cliente_id:
        query = query.filter(Caso.cliente_id == cliente_id)
    return query.order_by(Caso.atualizado_em.desc()).all()


@router.get("/casos/{caso_id}", response_model=CasoOut)
def obter_caso(
    caso_id: int,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    caso = db.query(Caso).filter(Caso.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso não encontrado")
    return caso


@router.patch("/casos/{caso_id}", response_model=CasoOut)
def atualizar_caso(
    caso_id: int,
    payload: CasoUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """
    Atualiza um caso — inclusive mover entre etapas do kanban
    (basta enviar {"etapa_funil": "proposta"}, por exemplo).
    """
    caso = db.query(Caso).filter(Caso.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso não encontrado")

    if payload.etapa_funil is not None:
        if payload.etapa_funil not in ETAPAS_FUNIL:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"etapa_funil deve ser uma de: {ETAPAS_FUNIL}",
            )
        caso.etapa_funil = payload.etapa_funil

    if payload.area_juridica is not None:
        caso.area_juridica = payload.area_juridica
    if payload.status is not None:
        caso.status = payload.status
    if payload.responsavel is not None:
        caso.responsavel = payload.responsavel
    if payload.resumo is not None:
        caso.resumo = payload.resumo

    db.commit()
    db.refresh(caso)
    registrar_log(db, acao="atualizar", entidade="caso", entidade_id=caso.id, usuario_email=admin.email)
    return caso


# ==================== KANBAN ====================

@router.get("/kanban", response_model=list[KanbanColuna])
def visao_kanban(
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Retorna os casos agrupados por etapa do funil, na ordem padrão do pipeline."""
    colunas = []
    for etapa in ETAPAS_FUNIL:
        casos = (
            db.query(Caso)
            .filter(Caso.etapa_funil == etapa, Caso.status == "aberto")
            .order_by(Caso.atualizado_em.desc())
            .all()
        )
        colunas.append({"etapa": etapa, "casos": casos})
    return colunas


# ==================== AUDITORIA ====================

@router.get("/auditoria")
def listar_auditoria(
    entidade: Optional[str] = None,
    limite: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Lista as entradas mais recentes de auditoria, opcionalmente filtradas por entidade."""
    query = db.query(LogAuditoria)
    if entidade:
        query = query.filter(LogAuditoria.entidade == entidade)
    logs = query.order_by(LogAuditoria.criado_em.desc()).limit(limite).all()
    return [
        {
            "id": log.id, "usuario_email": log.usuario_email, "acao": log.acao,
            "entidade": log.entidade, "entidade_id": log.entidade_id,
            "detalhes": log.detalhes, "criado_em": log.criado_em.isoformat(),
        }
        for log in logs
    ]
