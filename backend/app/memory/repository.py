"""Repositório de conversas — todo o acesso ao banco fica isolado aqui.

Padrão Repository: o serviço de memória não escreve SQL nem conhece o ORM;
ele apenas pede operações de alto nível (buscar lead, adicionar mensagem...).
Isso mantém baixo acoplamento e facilita testes.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.schemas import AIResponse
from app.db.models import Conversation, Lead, LeadStatus, Message, UsageLog


class ConversationRepository:
    """Operações de persistência sobre leads, conversas e mensagens."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_create_lead(
        self, phone: str, *, name: str | None = None, channel: str = "whatsapp"
    ) -> Lead:
        """Busca o lead pelo telefone; cria um novo se ainda não existir."""
        result = await self.session.execute(
            select(Lead).where(Lead.phone == phone)
        )
        lead = result.scalar_one_or_none()
        if lead is None:
            lead = Lead(
                phone=phone,
                name=name,
                channel=channel,
                status=LeadStatus.NOVO_LEAD,
            )
            self.session.add(lead)
            await self.session.flush()  # garante o lead.id preenchido
        elif name and not lead.name:
            # Enriquece o cadastro se o nome chegou depois.
            lead.name = name
        return lead

    async def get_or_create_conversation(self, lead: Lead) -> Conversation:
        """Retorna a conversa mais recente do lead; cria uma se não houver."""
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.lead_id == lead.id)
            .order_by(Conversation.id.desc())
        )
        conversation = result.scalars().first()
        if conversation is None:
            conversation = Conversation(lead_id=lead.id)
            self.session.add(conversation)
            await self.session.flush()
        return conversation

    async def get_messages(self, conversation_id: int) -> list[Message]:
        """Retorna o histórico completo da conversa, em ordem cronológica."""
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.id)
        )
        return list(result.scalars().all())

    async def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        *,
        provider: str | None = None,
        model: str | None = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
    ) -> Message:
        """Adiciona uma mensagem à conversa e retorna o registro criado."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        self.session.add(message)
        await self.session.flush()
        return message

    async def log_usage(
        self,
        response: AIResponse,
        *,
        lead_id: int | None = None,
        conversation_id: int | None = None,
    ) -> UsageLog:
        """Registra o uso da IA (CONTROLE DE CUSTOS) a partir de uma AIResponse."""
        log = UsageLog(
            lead_id=lead_id,
            conversation_id=conversation_id,
            provider=response.provider,
            model=response.model,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost_usd=response.cost_usd,
            latency_ms=response.latency_ms,
        )
        self.session.add(log)
        await self.session.flush()
        return log
