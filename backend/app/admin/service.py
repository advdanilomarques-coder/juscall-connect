"""Serviço administrativo — semente do admin, estatísticas e custos.

Concentra consultas de leitura para o dashboard (contagens, custos de IA,
conversas). Mantido separado das rotas para facilitar testes e reuso.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.core.security import hash_password
from app.db.base import SessionLocal
from app.db.models import (
    AdminUser,
    Conversation,
    Lead,
    LeadStatus,
    Message,
    UsageLog,
)

logger = get_logger(__name__)


async def seed_admin() -> None:
    """Cria o administrador inicial (a partir do .env) se ainda não existir.

    Executado no startup. A senha é armazenada apenas como hash bcrypt.
    """
    async with SessionLocal() as session:
        result = await session.execute(
            select(AdminUser).where(AdminUser.email == settings.admin_email)
        )
        if result.scalar_one_or_none() is not None:
            return
        admin = AdminUser(
            email=settings.admin_email,
            name="Administrador",
            password_hash=hash_password(settings.admin_password),
            is_active=True,
            is_superuser=True,
        )
        session.add(admin)
        await session.commit()
        logger.info("Administrador inicial criado: %s", settings.admin_email)


class AdminService:
    """Consultas de supervisão sobre um `AsyncSession`."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def dashboard(self) -> dict:
        """Números gerais do escritório para o painel inicial."""
        total_leads = await self.session.scalar(select(func.count(Lead.id)))
        total_messages = await self.session.scalar(select(func.count(Message.id)))
        total_cost = await self.session.scalar(
            select(func.coalesce(func.sum(UsageLog.cost_usd), 0.0))
        )
        total_tokens = await self.session.scalar(
            select(
                func.coalesce(
                    func.sum(UsageLog.input_tokens + UsageLog.output_tokens), 0
                )
            )
        )
        # Leads por etapa (para gráfico de funil).
        by_status_rows = await self.session.execute(
            select(Lead.status, func.count(Lead.id)).group_by(Lead.status)
        )
        by_status = {s.value: 0 for s in LeadStatus}
        for st, total in by_status_rows.all():
            by_status[st.value] = total

        return {
            "total_leads": total_leads or 0,
            "total_messages": total_messages or 0,
            "total_cost_usd": round(total_cost or 0.0, 4),
            "total_tokens": total_tokens or 0,
            "leads_por_etapa": by_status,
        }

    async def usage_by_provider(self) -> list[dict]:
        """Custos e tokens agregados por provedor de IA (controle de custos)."""
        rows = await self.session.execute(
            select(
                UsageLog.provider,
                func.count(UsageLog.id),
                func.coalesce(func.sum(UsageLog.input_tokens), 0),
                func.coalesce(func.sum(UsageLog.output_tokens), 0),
                func.coalesce(func.sum(UsageLog.cost_usd), 0.0),
                func.coalesce(func.avg(UsageLog.latency_ms), 0),
            ).group_by(UsageLog.provider)
        )
        return [
            {
                "provider": provider,
                "requests": requests,
                "input_tokens": in_tok,
                "output_tokens": out_tok,
                "cost_usd": round(cost, 5),
                "avg_latency_ms": int(avg_lat or 0),
            }
            for provider, requests, in_tok, out_tok, cost, avg_lat in rows.all()
        ]

    async def conversation_messages(self, lead_id: int) -> list[Message]:
        """Histórico completo de mensagens de um lead (para supervisão)."""
        conv = await self.session.execute(
            select(Conversation.id)
            .where(Conversation.lead_id == lead_id)
            .order_by(Conversation.id.desc())
        )
        conv_id = conv.scalars().first()
        if conv_id is None:
            return []
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conv_id)
            .order_by(Message.id)
        )
        return list(result.scalars().all())
