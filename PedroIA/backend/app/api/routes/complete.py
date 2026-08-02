from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import CompletionRequest, CompletionResponse
from app.auth.security import require_api_key
from app.database.session import get_session
from app.llm_engine.router import get_router
from app.monitoring.usage import log_usage

router = APIRouter(tags=["completion"], dependencies=[Depends(require_api_key)])


@router.post("/complete", response_model=CompletionResponse)
async def complete(req: CompletionRequest, db: AsyncSession = Depends(get_session)) -> CompletionResponse:
    result = await get_router().complete(
        prefix=req.prefix,
        suffix=req.suffix,
        language=req.language,
        mode=req.mode,
        max_tokens=req.max_tokens,
    )
    await log_usage(
        db, session_id="completion", kind="complete", provider=result.provider, model=result.model, mode=req.mode
    )
    return CompletionResponse(completion=result.content, model=result.model)
