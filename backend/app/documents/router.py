"""Rotas de documentos (painel administrativo — protegidas por JWT).

Permite ao administrador enviar/baixar/listar documentos de um lead. O
recebimento automático via WhatsApp usa diretamente o `DocumentService`.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_admin, get_session
from app.documents.service import DocumentService

router = APIRouter(
    prefix="/documents",
    tags=["Documentos"],
    dependencies=[Depends(get_current_admin)],
)


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    doc_type: str
    filename: str
    content_type: str | None
    size_bytes: int
    created_at: datetime


@router.post("/leads/{lead_id}", response_model=DocumentOut, status_code=201)
async def upload_document(
    lead_id: int,
    doc_type: str = Form("outro"),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
) -> DocumentOut:
    """Faz upload de um documento (CPF, RG, extrato...) para um lead."""
    data = await file.read()
    document = await DocumentService(session).store(
        lead_id,
        doc_type,
        file.filename or "arquivo",
        data,
        content_type=file.content_type,
    )
    await session.commit()
    return DocumentOut.model_validate(document)


@router.get("/leads/{lead_id}", response_model=list[DocumentOut])
async def list_documents(
    lead_id: int, session: AsyncSession = Depends(get_session)
) -> list[DocumentOut]:
    docs = await DocumentService(session).list_for_lead(lead_id)
    return [DocumentOut.model_validate(d) for d in docs]


@router.get("/{document_id}/download")
async def download_document(
    document_id: int, session: AsyncSession = Depends(get_session)
) -> FileResponse:
    """Baixa o arquivo físico de um documento."""
    document = await DocumentService(session).get(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    return FileResponse(
        document.path,
        filename=document.filename,
        media_type=document.content_type or "application/octet-stream",
    )
