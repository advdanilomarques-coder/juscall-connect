"""Serviço de documentos — grava o arquivo no disco e o metadado no banco.

Reaproveitado tanto pelo upload do painel administrativo quanto pelo
recebimento de mídia via WhatsApp: a lógica de "guardar um documento de um
lead" mora num único lugar.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document, Lead, LeadStatus
from app.documents import storage
from app.core.logging import get_logger

logger = get_logger(__name__)


class DocumentService:
    """Operações de documentos sobre um `AsyncSession`."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def store(
        self,
        lead_id: int,
        doc_type: str,
        filename: str,
        data: bytes,
        *,
        content_type: str | None = None,
    ) -> Document:
        """Salva o arquivo e registra seus metadados vinculados ao lead."""
        path, size = storage.save(lead_id, doc_type, filename, data)
        document = Document(
            lead_id=lead_id,
            doc_type=doc_type,
            filename=filename,
            path=path,
            content_type=content_type,
            size_bytes=size,
        )
        self.session.add(document)

        # Ao receber documentos, o lead avança para "documentação recebida"
        # (se ainda estiver numa etapa anterior a essa).
        lead = await self.session.get(Lead, lead_id)
        if lead is not None and lead.status in (
            LeadStatus.NOVO_LEAD,
            LeadStatus.PRIMEIRO_ATENDIMENTO,
            LeadStatus.ANALISE_JURIDICA,
            LeadStatus.DOCUMENTACAO_PENDENTE,
        ):
            lead.status = LeadStatus.DOCUMENTACAO_RECEBIDA

        await self.session.flush()
        logger.info("Documento '%s' (%s) salvo para lead %s.", filename, doc_type, lead_id)
        return document

    async def list_for_lead(self, lead_id: int) -> list[Document]:
        result = await self.session.execute(
            select(Document)
            .where(Document.lead_id == lead_id)
            .order_by(Document.id.desc())
        )
        return list(result.scalars().all())

    async def get(self, document_id: int) -> Document | None:
        return await self.session.get(Document, document_id)
