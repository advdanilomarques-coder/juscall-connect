"""Rotas do painel administrativo.

  * POST /admin/login          → autentica e devolve o token JWT (público).
  * GET  /admin/me             → dados do admin logado (protegido).
  * GET  /admin/dashboard      → números gerais do escritório (protegido).
  * GET  /admin/usage          → custos/tokens por provedor de IA (protegido).
  * GET  /admin/providers      → provedores de IA disponíveis (protegido).
  * GET  /admin/leads/{id}/messages → histórico de conversa (protegido).
  * POST /admin/reply          → o admin responde manualmente ao cliente.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.service import AdminService
from app.ai.manager import ai_manager
from app.channels.whatsapp import whatsapp_client
from app.core.security import create_access_token, verify_password
from app.db.models import AdminUser, Conversation, Lead, Message
from app.deps import get_current_admin, get_session

router = APIRouter(prefix="/admin", tags=["Painel Administrativo"])


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    provider: str | None
    model: str | None
    created_at: datetime


class ReplyRequest(BaseModel):
    lead_id: int
    message: str = Field(..., min_length=1)
    send_whatsapp: bool = Field(
        default=True, description="Também enviar via WhatsApp ao cliente."
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest, session: AsyncSession = Depends(get_session)
) -> TokenResponse:
    """Autentica o administrador e devolve um token JWT."""
    result = await session.execute(
        select(AdminUser).where(AdminUser.email == data.email)
    )
    admin = result.scalar_one_or_none()
    if admin is None or not verify_password(data.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
        )
    if not admin.is_active:
        raise HTTPException(status_code=403, detail="Usuário inativo.")
    token = create_access_token(admin.email, extra={"name": admin.name})
    return TokenResponse(access_token=token)


@router.get("/me")
async def me(admin: AdminUser = Depends(get_current_admin)) -> dict:
    """Retorna os dados do administrador autenticado."""
    return {
        "id": admin.id,
        "email": admin.email,
        "name": admin.name,
        "is_superuser": admin.is_superuser,
    }


@router.get("/dashboard", dependencies=[Depends(get_current_admin)])
async def dashboard(session: AsyncSession = Depends(get_session)) -> dict:
    """Números gerais: leads, mensagens, custo total, tokens, funil."""
    return await AdminService(session).dashboard()


@router.get("/usage", dependencies=[Depends(get_current_admin)])
async def usage(session: AsyncSession = Depends(get_session)) -> list[dict]:
    """Custos e tokens agregados por provedor de IA (CONTROLE DE CUSTOS)."""
    return await AdminService(session).usage_by_provider()


@router.get("/providers", dependencies=[Depends(get_current_admin)])
async def providers() -> dict:
    """Lista os provedores de IA configurados e os disponíveis."""
    return {"available": ai_manager.available_providers}


@router.get(
    "/leads/{lead_id}/messages",
    response_model=list[MessageOut],
    dependencies=[Depends(get_current_admin)],
)
async def conversation_messages(
    lead_id: int, session: AsyncSession = Depends(get_session)
) -> list[MessageOut]:
    """Histórico completo de mensagens de um lead (supervisão)."""
    messages = await AdminService(session).conversation_messages(lead_id)
    return [
        MessageOut(
            id=m.id,
            role=m.role,
            content=m.content,
            provider=m.provider,
            model=m.model,
            created_at=m.created_at,
        )
        for m in messages
    ]


@router.post("/reply", dependencies=[Depends(get_current_admin)])
async def reply(
    data: ReplyRequest, session: AsyncSession = Depends(get_session)
) -> dict:
    """O administrador responde manualmente ao cliente (assumindo o caso).

    Registra a mensagem no histórico como se fosse do agente e, opcionalmente,
    a envia pelo WhatsApp. Não passa pela IA — é texto humano.
    """
    lead = await session.get(Lead, data.lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead não encontrado.")

    # Localiza (ou cria) a conversa mais recente do lead.
    result = await session.execute(
        select(Conversation)
        .where(Conversation.lead_id == lead.id)
        .order_by(Conversation.id.desc())
    )
    conversation = result.scalars().first()
    if conversation is None:
        conversation = Conversation(lead_id=lead.id)
        session.add(conversation)
        await session.flush()

    session.add(
        Message(
            conversation_id=conversation.id,
            role="assistant",
            content=data.message,
            provider="human",
            model="admin",
        )
    )
    await session.commit()

    if data.send_whatsapp and lead.channel == "whatsapp":
        await whatsapp_client.send_text(lead.phone, data.message)

    return {"status": "sent"}
