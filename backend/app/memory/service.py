"""Serviço de Memória — orquestra o fluxo completo de um turno de conversa.

Fluxo de `handle_turn`:
  1. Identifica (ou cria) o lead pelo telefone.
  2. Recupera o histórico da conversa no banco.
  3. Persiste a mensagem do cliente.
  4. Chama a camada de IA com TODO o contexto (histórico + nova mensagem).
  5. Persiste a resposta do agente (com metadados de custo).
  6. Registra o uso para controle de custos (UsageLog).
  7. Avança o status do lead no funil, quando aplicável.

Como o histórico vem do banco e é neutro, a troca de modelo de IA (failover)
nunca faz o agente "esquecer" a conversa (MEMÓRIA UNIFICADA).
"""

from __future__ import annotations

from app.ai.manager import AIManager, ai_manager
from app.ai.schemas import AIMessage, AIResponse, Role, TaskType
from app.core.logging import get_logger
from app.db.base import SessionLocal
from app.db.models import LeadStatus
from app.memory.repository import ConversationRepository

logger = get_logger(__name__)


class MemoryService:
    """Une persistência e IA para produzir uma resposta com memória."""

    def __init__(
        self,
        *,
        session_factory=SessionLocal,
        manager: AIManager | None = None,
    ) -> None:
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
        channel: str = "whatsapp",
        task: TaskType | None = TaskType.ATENDIMENTO,
    ) -> AIResponse:
        """Processa uma mensagem do cliente e devolve a resposta do agente."""
        async with self._session_factory() as session:
            repo = ConversationRepository(session)

            lead = await repo.get_or_create_lead(phone, name=name, channel=channel)
            conversation = await repo.get_or_create_conversation(lead)
            lead_id = lead.id
            conversation_id = conversation.id
            human_takeover = lead.human_takeover

            # 1) Monta o contexto: histórico salvo + a nova mensagem do cliente.
            history = await repo.get_messages(conversation_id)
            ai_messages: list[AIMessage] = [
                AIMessage(role=Role(m.role), content=m.content)
                for m in history
                if m.role in (Role.USER.value, Role.ASSISTANT.value)
            ]
            ai_messages.append(AIMessage(role=Role.USER, content=text))

            # 2) Persiste a mensagem do cliente e confirma (memória preservada
            #    mesmo se a IA falhar depois).
            await repo.add_message(conversation_id, Role.USER.value, text)
            await session.commit()

            # Se um atendente humano assumiu o caso, o agente NÃO responde
            # automaticamente — apenas registra a mensagem do cliente.
            if human_takeover:
                logger.info("Lead %s em atendimento humano — IA silenciada.", lead_id)
                return AIResponse(
                    content="", provider="human", model="takeover"
                )

            # 3) Chama a IA (pode acionar retry + failover internamente).
            response = await self._manager.generate(
                ai_messages, system=system, task=task
            )

            # 4) Persiste a resposta do agente com metadados de custo.
            await repo.add_message(
                conversation_id,
                Role.ASSISTANT.value,
                response.content,
                provider=response.provider,
                model=response.model,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
            )

            # 5) Registra o uso para controle de custos.
            await repo.log_usage(
                response, lead_id=lead_id, conversation_id=conversation_id
            )

            # 6) Avança o status do funil no primeiro atendimento respondido.
            if lead.status == LeadStatus.NOVO_LEAD:
                lead.status = LeadStatus.PRIMEIRO_ATENDIMENTO

            await session.commit()
            return response


# Instância única compartilhada pela aplicação.
memory_service = MemoryService()
