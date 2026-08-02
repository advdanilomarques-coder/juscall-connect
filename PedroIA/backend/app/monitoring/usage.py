"""Usage logging used by the CRM/monitoring layer."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import UsageLog


async def log_usage(
    db: AsyncSession,
    *,
    session_id: str,
    kind: str,
    provider: str = "",
    model: str = "",
    mode: str = "",
    status: str = "ok",
    detail: str = "",
) -> None:
    db.add(
        UsageLog(
            session_id=session_id or "",
            kind=kind,
            provider=provider,
            model=model,
            mode=mode,
            status=status,
            detail=detail[:500],
        )
    )
    await db.commit()
