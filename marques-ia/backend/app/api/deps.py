# -*- coding: utf-8 -*-
"""Dependências compartilhadas dos endpoints protegidos por JWT."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database.session import get_db
from app.models.user import AdminUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> AdminUser:
    email = decode_access_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

    user = db.query(AdminUser).filter(AdminUser.email == email).first()
    if not user or not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inválido ou inativo",
        )

    return user


def require_admin(usuario: AdminUser = Depends(get_current_admin)) -> AdminUser:
    """
    Restringe o acesso a usuários com papel 'admin' (o dono).
    Funcionários (papel 'funcionario') recebem 403 nestas rotas — eles só
    têm acesso à área de clientes.
    """
    if usuario.papel != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito ao administrador.",
        )
    return usuario
