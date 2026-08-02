"""Lightweight CRM/monitoring read API: usage, errors, conversations."""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Conversation, UsageLog
from app.database.session import get_session

router = APIRouter(tags=["crm"], prefix="/crm")


@router.get("/summary")
async def summary(db: AsyncSession = Depends(get_session)) -> dict:
    total = await db.scalar(select(func.count(UsageLog.id)))
    errors = await db.scalar(select(func.count(UsageLog.id)).where(UsageLog.status == "error"))
    convos = await db.scalar(select(func.count(Conversation.id)))
    by_provider = await db.execute(
        select(UsageLog.provider, func.count(UsageLog.id)).group_by(UsageLog.provider)
    )
    return {
        "requests_total": total or 0,
        "errors_total": errors or 0,
        "conversations_total": convos or 0,
        "by_provider": {p or "unknown": c for p, c in by_provider.all()},
    }


@router.get("/logs")
async def logs(limit: int = 50, db: AsyncSession = Depends(get_session)) -> List[dict]:
    rows = await db.execute(select(UsageLog).order_by(UsageLog.created_at.desc()).limit(limit))
    return [
        {
            "id": r.id,
            "kind": r.kind,
            "provider": r.provider,
            "model": r.model,
            "mode": r.mode,
            "status": r.status,
            "detail": r.detail,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows.scalars().all()
    ]
