# -*- coding: utf-8 -*-
"""Autenticação e gestão de usuários do painel administrativo."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, require_admin
from app.core.audit import registrar_log
from app.core.security import create_access_token, hash_password, verify_password
from app.database.session import get_db
from app.models.user import AdminUser
from app.schemas.auth import TokenResponse, UsuarioCreate, UsuarioOut

router = APIRouter(prefix="/auth", tags=["autenticação"])

PAPEIS_VALIDOS = {"admin", "funcionario"}


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Login: usuário = e-mail, senha = senha cadastrada."""
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
    return TokenResponse(access_token=token, papel=user.papel, nome=user.nome)


@router.get("/me", response_model=UsuarioOut)
def usuario_atual(usuario: AdminUser = Depends(get_current_admin)):
    """Retorna os dados do usuário logado (usado pelo painel para ajustar o acesso)."""
    return usuario


# ==================== GESTÃO DE USUÁRIOS (somente admin) ====================

@router.get("/usuarios", response_model=list[UsuarioOut])
def listar_usuarios(
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(require_admin),
):
    return db.query(AdminUser).order_by(AdminUser.id).all()


@router.post("/usuarios", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def criar_usuario(
    payload: UsuarioCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """Cria um novo usuário (funcionário ou admin). Apenas o admin pode fazer isso."""
    papel = payload.papel if payload.papel in PAPEIS_VALIDOS else "funcionario"

    email = payload.email.strip().lower()
    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="E-mail inválido.")

    if db.query(AdminUser).filter(AdminUser.email == email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um usuário com este e-mail.")

    if len(payload.senha) < 6:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="A senha deve ter ao menos 6 caracteres.")

    novo = AdminUser(
        nome=payload.nome.strip() or email,
        email=email,
        senha_hash=hash_password(payload.senha),
        papel=papel,
        ativo=True,
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    registrar_log(
        db, acao="criar_usuario", entidade="usuario_admin",
        entidade_id=novo.id, usuario_email=admin.email, detalhes=f"papel={papel}",
    )
    return novo


@router.delete("/usuarios/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    """Remove um usuário. O admin não pode remover a si mesmo."""
    if usuario_id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Você não pode remover a si mesmo.")

    usuario = db.query(AdminUser).filter(AdminUser.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    db.delete(usuario)
    registrar_log(
        db, acao="remover_usuario", entidade="usuario_admin",
        entidade_id=usuario_id, usuario_email=admin.email, detalhes=f"email={usuario.email}",
    )
    db.commit()
    return None
