"""Conversation memory. Persists turns so PedroIA remembers past sessions.

This is the durable-memory piece. A future step layers embeddings + a vector store
(pgvector / LlamaIndex) on top for semantic recall; the interface here stays the same.
"""
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Conversation, ConversationMessage


async def get_or_create_conversation(db: AsyncSession, session_id: str) -> Conversation:
    result = await db.execute(select(Conversation).where(Conversation.session_id == session_id))
    convo = result.scalar_one_or_none()
    if convo is None:
        convo = Conversation(session_id=session_id, title="")
        db.add(convo)
        await db.flush()
    return convo


async def save_turn(db: AsyncSession, session_id: str, role: str, content: str) -> None:
    convo = await get_or_create_conversation(db, session_id)
    if not convo.title and role == "user":
        convo.title = content[:80]
    db.add(ConversationMessage(conversation_id=convo.id, role=role, content=content))
    await db.commit()


async def recent_history(db: AsyncSession, session_id: str, limit: int = 20) -> List[ConversationMessage]:
    result = await db.execute(select(Conversation).where(Conversation.session_id == session_id))
    convo = result.scalar_one_or_none()
    if convo is None:
        return []
    msgs = await db.execute(
        select(ConversationMessage)
        .where(ConversationMessage.conversation_id == convo.id)
        .order_by(ConversationMessage.created_at.desc())
        .limit(limit)
    )
    return list(reversed(msgs.scalars().all()))
