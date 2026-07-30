# -*- coding: utf-8 -*-
"""
Endpoints de documentos: upload de anexos (imagem ou PDF) vinculados a um
caso, com extração automática de texto via OCR.
"""
import os
import shutil

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.audit import registrar_log
from app.database.session import get_db
from app.documents.ocr import LIMIAR_CONFIANCA_BAIXA, processar_documento
from app.models.case import Caso
from app.models.document import Documento
from app.models.user import AdminUser
from app.schemas.document import DocumentoOut, DocumentoUploadResponse

router = APIRouter(prefix="/documentos", tags=["documentos"])

STORAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "storage", "documentos")
EXTENSOES_PDF = {".pdf"}
EXTENSOES_IMAGEM = {".png", ".jpg", ".jpeg"}


@router.post("/upload", response_model=DocumentoUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_documento(
    caso_id: int = Form(...),
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """
    Recebe um arquivo (PDF ou imagem), salva em disco, roda OCR e vincula
    o texto extraído ao caso informado. Documentos com baixa confiança de
    OCR são sinalizados para revisão manual (revisao_manual_recomendada=true).
    """
    caso = db.query(Caso).filter(Caso.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso não encontrado")

    extensao = os.path.splitext(arquivo.filename or "")[1].lower()
    if extensao in EXTENSOES_PDF:
        tipo = "pdf"
    elif extensao in EXTENSOES_IMAGEM:
        tipo = "image"
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Formato não suportado. Envie um arquivo PDF, PNG ou JPG.",
        )

    os.makedirs(os.path.abspath(STORAGE_DIR), exist_ok=True)
    nome_salvo = f"caso{caso_id}_{arquivo.filename}"
    caminho_absoluto = os.path.abspath(os.path.join(STORAGE_DIR, nome_salvo))

    with open(caminho_absoluto, "wb") as destino:
        shutil.copyfileobj(arquivo.file, destino)

    texto_extraido, confianca = processar_documento(caminho_absoluto, tipo)

    documento = Documento(
        caso_id=caso_id,
        nome_arquivo=arquivo.filename,
        tipo=tipo,
        caminho_arquivo=os.path.join("storage", "documentos", nome_salvo),
        texto_ocr=texto_extraido,
        confianca_ocr=confianca,
    )
    db.add(documento)
    db.commit()
    db.refresh(documento)

    registrar_log(
        db, acao="upload_documento", entidade="documento",
        entidade_id=documento.id, usuario_email=admin.email, detalhes=f"caso_id={caso_id}",
    )

    preview = texto_extraido[:300] + ("..." if len(texto_extraido) > 300 else "")
    return DocumentoUploadResponse(
        id=documento.id,
        nome_arquivo=documento.nome_arquivo,
        texto_extraido_preview=preview,
        confianca_ocr=round(confianca, 1),
        revisao_manual_recomendada=confianca < LIMIAR_CONFIANCA_BAIXA,
    )


@router.get("/{documento_id}", response_model=DocumentoOut)
def obter_documento(
    documento_id: int,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    documento = db.query(Documento).filter(Documento.id == documento_id).first()
    if not documento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")
    return documento


@router.get("/caso/{caso_id}", response_model=list[DocumentoOut])
def listar_documentos_do_caso(
    caso_id: int,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    return db.query(Documento).filter(Documento.caso_id == caso_id).order_by(Documento.upload_em.desc()).all()
