"""User authentication endpoints for the website: register, login, me."""
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.passwords import create_access_token, decode_token, hash_password, verify_password
from app.core.config import get_settings
from app.database.models import User
from app.database.session import get_session

router = APIRouter(tags=["auth"], prefix="/auth")


def _valid_email(v: str) -> str:
    v = v.strip().lower()
    if "@" not in v or "." not in v.split("@")[-1] or len(v) < 5:
        raise ValueError("E-mail inválido.")
    return v


class RegisterIn(BaseModel):
    email: str
    password: str = Field(..., min_length=6, max_length=128)
    display_name: str = Field(default="", max_length=120)

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        return _valid_email(v)


class LoginIn(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        return _valid_email(v)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str
    display_name: str


class UserOut(BaseModel):
    email: str
    display_name: str


async def _get_user(db: AsyncSession, email: str) -> User | None:
    res = await db.execute(select(User).where(User.email == email.lower()))
    return res.scalar_one_or_none()


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterIn, db: AsyncSession = Depends(get_session)) -> TokenOut:
    if not get_settings().allow_signup:
        raise HTTPException(status_code=403, detail="Cadastro desabilitado.")
    email = body.email.lower()
    if await _get_user(db, email):
        raise HTTPException(status_code=409, detail="Este e-mail já está cadastrado.")
    user = User(email=email, display_name=body.display_name or email.split("@")[0])
    # Store the hash in a dedicated column added to the model.
    user.password_hash = hash_password(body.password)
    db.add(user)
    await db.commit()
    token = create_access_token(email)
    return TokenOut(access_token=token, email=email, display_name=user.display_name)


@router.post("/login", response_model=TokenOut)
async def login(body: LoginIn, db: AsyncSession = Depends(get_session)) -> TokenOut:
    user = await _get_user(db, body.email.lower())
    if not user or not user.password_hash or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")
    token = create_access_token(user.email)
    return TokenOut(access_token=token, email=user.email, display_name=user.display_name)


@router.get("/me", response_model=UserOut)
async def me(authorization: str = Header(default=""), db: AsyncSession = Depends(get_session)) -> UserOut:
    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_token(token) if token else None
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Sessão inválida.")
    user = await _get_user(db, str(payload["sub"]))
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return UserOut(email=user.email, display_name=user.display_name)
