# -*- coding: utf-8 -*-
"""Endpoint de autenticação do painel administrativo."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.audit import registrar_log
from app.core.security import create_access_token, verify_password
from app.database.session import get_db
from app.models.user import AdminUser
from app.schemas.auth import TokenResponse

router = APIRouter(prefix="/auth", tags=["autenticação"])


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Login do administrador: usuário = e-mail, senha = ADMIN_DEFAULT_PASSWORD (ou já trocada)."""
    user = db.query(AdminUser).filter(AdminUser.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos",
        )

    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário desativado",
        )

    token = create_access_token(subject=user.email)
    registrar_log(db, acao="login", entidade="usuario_admin", entidade_id=user.id, usuario_email=user.email)
    return TokenResponse(access_token=token)
