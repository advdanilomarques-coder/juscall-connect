"""Serviço de Memória — orquestra o fluxo completo de um turno de conversa.

Fluxo de `handle_turn`:
  1. Identifica (ou cria) o lead pelo telefone.
  2. Recupera o histórico da conversa no banco.
  3. Persiste a mensagem do cliente.
  4. Chama a camada de IA com TODO o contexto (histórico + nova mensagem).
  5. Persiste a resposta do agente (com metadados de custo).
  6. Avança o status do lead no funil, quando aplicável.

Como o histórico vem do banco e é neutro, a troca de modelo de IA (failover)
nunca faz o agente "esquecer" a conversa.
"""

from __future__ import annotations

from app.ai.manager import AIManager, ai_manager
from app.ai.schemas import AIMessage, AIResponse, Role
from app.core.logging import get_logger
from app.db.base import SessionLocal
from app.db.models import LeadStatus
from app.memory.repository import ConversationRepository

logger = get_logger(__name__)


class MemoryService:
    """Une persistência e IA para produzir uma resposta com memória."""

    def __init__(self, *, session_factory=SessionLocal, manager: AIManager | None = None) -> None:
        # Injeção de dependência: em testes passamos uma fábrica de sessões e
        # um gerenciador falso; em produção usamos os padrões globais.
        self._session_factory = session_factory
        self._manager = manager or ai_manager

    async def handle_turn(
        self,
        phone: str,
        text: str,
        *,
        system: str | None = None,
        name: str | None = None,
    ) -> AIResponse:
        """Processa uma mensagem do cliente e devolve a resposta do agente."""
        async with self._session_factory() as session:
            repo = ConversationRepository(session)

            lead = await repo.get_or_create_lead(phone, name=name)
            conversation = await repo.get_or_create_conversation(lead)

            # 1) Monta o contexto: histórico salvo + a nova mensagem do cliente.
            history = await repo.get_messages(conversation.id)
            ai_messages: list[AIMessage] = [
                AIMessage(role=Role(m.role), content=m.content) for m in history
            ]
            ai_messages.append(AIMessage(role=Role.USER, content=text))

            # 2) Persiste a mensagem do cliente e confirma (memória preservada
            #    mesmo se a IA falhar depois).
            await repo.add_message(conversation.id, Role.USER.value, text)
            await session.commit()

            # 3) Chama a IA (pode acionar failover internamente).
            response = await self._manager.generate(ai_messages, system=system)

            # 4) Persiste a resposta do agente com metadados de custo.
            await repo.add_message(
                conversation.id,
                Role.ASSISTANT.value,
                response.content,
                provider=response.provider,
                model=response.model,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
            )

            # 5) Avança o status do funil no primeiro atendimento respondido.
            if lead.status == LeadStatus.NOVO_LEAD:
                lead.status = LeadStatus.PRIMEIRO_ATENDIMENTO

            await session.commit()
            return response


# Instância única compartilhada pela aplicação.
memory_service = MemoryService()
