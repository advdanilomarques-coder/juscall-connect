from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import ChatRequest, ChatResponse
from app.auth.security import require_api_key
from app.database.session import get_session
from app.llm_engine.prompts import build_system_prompt, format_context
from app.llm_engine.providers import Message
from app.llm_engine.router import get_router
from app.memory.store import save_turn
from app.monitoring.usage import log_usage

router = APIRouter(tags=["chat"], dependencies=[Depends(require_api_key)])


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_session)) -> ChatResponse:
    last_user = next((m.content for m in reversed(req.messages) if m.role == "user"), "")
    context_block = format_context(req.context.model_dump() if req.context else None)
    system_prompt = build_system_prompt(last_user, context_block)

    # Rebuild the message list with our engineered system prompt at the front.
    messages = [Message("system", system_prompt)]
    for m in req.messages:
        if m.role == "system":
            continue
        messages.append(Message(m.role, m.content))

    router_ = get_router()
    session_id = req.session_id or "anonymous"
    try:
        result = await router_.chat(messages, mode=req.mode, max_tokens=req.max_tokens)
    except Exception as e:  # noqa: BLE001
        await log_usage(db, session_id=session_id, kind="chat", mode=req.mode, status="error", detail=str(e))
        raise

    if req.session_id:
        await save_turn(db, session_id, "user", last_user)
        await save_turn(db, session_id, "assistant", result.content)
    await log_usage(
        db, session_id=session_id, kind="chat", provider=result.provider, model=result.model, mode=req.mode
    )

    return ChatResponse(content=result.content, model=result.model, provider=result.provider, mode=req.mode)
