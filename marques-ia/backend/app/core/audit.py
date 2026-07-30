# -*- coding: utf-8 -*-
"""Função utilitária para registrar entradas na tabela de auditoria."""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.audit_log import LogAuditoria


def registrar_log(
    db: Session,
    acao: str,
    entidade: str,
    entidade_id: Optional[int] = None,
    usuario_email: Optional[str] = None,
    detalhes: Optional[str] = None,
) -> None:
    """Grava uma linha de auditoria. Não interrompe o fluxo principal em caso de erro."""
    try:
        log = LogAuditoria(
            usuario_email=usuario_email,
            acao=acao,
            entidade=entidade,
            entidade_id=entidade_id,
            detalhes=detalhes,
        )
        db.add(log)
        db.commit()
    except Exception:  # noqa: BLE001 — auditoria nunca deve derrubar a requisição principal
        db.rollback()
