# -*- coding: utf-8 -*-
"""
Endpoints de contratos: geração automática em PDF, aprovação humana obrigatória
antes do envio, e download do arquivo gerado.
"""
import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import require_admin as get_current_admin
from app.contracts.generator import gerar_pdf_contrato
from app.contracts.templates import TEMPLATES, TIPOS_DISPONIVEIS
from app.core.audit import registrar_log
from app.core.config import settings
from app.database.session import get_db
from app.integrations.email_client import EmailError, enviar_email
from app.models.case import Caso
from app.models.client import Cliente
from app.models.contract import Contrato
from app.models.user import AdminUser
from app.schemas.contract import ContratoEnviarResponse, ContratoGerarRequest, ContratoOut

router = APIRouter(prefix="/contratos", tags=["contratos"])


@router.get("/tipos")
def listar_tipos_contrato(_admin: AdminUser = Depends(get_current_admin)):
    """Lista os tipos de contrato disponíveis e seus títulos (usado pelo painel)."""
    return [{"tipo": tipo, "titulo": dados["titulo"]} for tipo, dados in TEMPLATES.items()]


@router.get("")
def listar_contratos(
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Lista todos os contratos com dados do cliente/caso — usado pela aba Contratos do painel."""
    contratos = db.query(Contrato).order_by(Contrato.gerado_em.desc()).all()
    resultado = []
    for c in contratos:
        caso = db.query(Caso).filter(Caso.id == c.caso_id).first()
        cliente = db.query(Cliente).filter(Cliente.id == caso.cliente_id).first() if caso else None
        resultado.append({
            "id": c.id,
            "numero": c.numero,
            "tipo": c.tipo,
            "status": c.status,
            "caso_id": c.caso_id,
            "gerado_em": c.gerado_em.isoformat() if c.gerado_em else None,
            "cliente_nome": cliente.nome if cliente else None,
            "cliente_email": cliente.email if cliente else None,
        })
    return resultado


@router.post("/gerar", response_model=ContratoOut, status_code=status.HTTP_201_CREATED)
def gerar_contrato(
    payload: ContratoGerarRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    if payload.tipo not in TIPOS_DISPONIVEIS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Tipo de contrato deve ser um de: {TIPOS_DISPONIVEIS}",
        )

    caso = db.query(Caso).filter(Caso.id == payload.caso_id).first()
    if not caso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso não encontrado")

    cliente = db.query(Cliente).filter(Cliente.id == caso.cliente_id).first()

    # Cria o registro primeiro para obter o ID usado no número do contrato.
    contrato = Contrato(caso_id=caso.id, tipo=payload.tipo, arquivo_pdf_path="", status="rascunho")
    db.add(contrato)
    db.commit()
    db.refresh(contrato)

    caminho_relativo = gerar_pdf_contrato(
        contrato_id=contrato.id,
        tipo=payload.tipo,
        nome_cliente=cliente.nome if cliente else None,
        numero_caso=caso.id,
        resumo_caso=caso.resumo,
    )

    from app.contracts.generator import gerar_numero_contrato
    contrato.arquivo_pdf_path = caminho_relativo
    contrato.numero = gerar_numero_contrato(contrato.id)
    db.commit()
    db.refresh(contrato)

    # Contrato gerado avança o caso para a etapa "contrato" no kanban.
    caso.etapa_funil = "contrato"
    db.commit()

    registrar_log(
        db, acao="gerar_contrato", entidade="contrato",
        entidade_id=contrato.id, usuario_email=admin.email, detalhes=f"caso_id={caso.id}",
    )

    return contrato


@router.get("/{contrato_id}", response_model=ContratoOut)
def obter_contrato(
    contrato_id: int,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrato não encontrado")
    return contrato


@router.patch("/{contrato_id}/aprovar", response_model=ContratoOut)
def aprovar_contrato(
    contrato_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """
    Marca o contrato como aprovado por um advogado responsável — passo
    obrigatório antes de qualquer envio ao cliente.
    """
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrato não encontrado")

    contrato.status = "aprovado"
    db.commit()
    db.refresh(contrato)
    registrar_log(
        db, acao="aprovar_contrato", entidade="contrato",
        entidade_id=contrato.id, usuario_email=admin.email,
    )
    return contrato


@router.post("/{contrato_id}/enviar", response_model=ContratoEnviarResponse)
def enviar_contrato_por_email(
    contrato_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """
    Envia o PDF do contrato APROVADO para o e-mail do cliente e marca o
    contrato como 'enviado'. Exige que o contrato já tenha sido aprovado por
    um advogado (status='aprovado') e que o cliente tenha e-mail cadastrado.
    """
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrato não encontrado")

    if contrato.status not in ("aprovado", "enviado"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="O contrato precisa ser aprovado por um advogado antes de ser enviado ao cliente.",
        )

    caso = db.query(Caso).filter(Caso.id == contrato.caso_id).first()
    cliente = db.query(Cliente).filter(Cliente.id == caso.cliente_id).first() if caso else None
    if not cliente or not cliente.email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O cliente deste caso não tem e-mail cadastrado. Cadastre o e-mail no CRM antes de enviar.",
        )

    if not settings.EMAIL_HABILITADO:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Envio de e-mail desativado: configure SMTP_HOST/SMTP_USER/SMTP_PASSWORD no .env.",
        )

    caminho_pdf = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", contrato.arquivo_pdf_path)
    )
    if not os.path.isfile(caminho_pdf):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo do contrato não encontrado em disco.",
        )

    nome = cliente.nome or "Cliente"
    assunto = f"{settings.SMTP_FROM_NAME} — Contrato {contrato.numero}"
    corpo = (
        f"Prezado(a) {nome},\n\n"
        f"Segue em anexo o contrato {contrato.numero} referente ao seu atendimento.\n"
        f"Por favor, revise o documento. Qualquer dúvida, estamos à disposição.\n\n"
        f"Atenciosamente,\n{settings.SMTP_FROM_NAME}"
    )

    try:
        enviar_email(destino=cliente.email, assunto=assunto, corpo=corpo, anexos=[caminho_pdf])
    except EmailError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Falha ao enviar o e-mail: {exc}",
        )

    contrato.status = "enviado"
    db.commit()
    db.refresh(contrato)

    registrar_log(
        db, acao="enviar_contrato_email", entidade="contrato",
        entidade_id=contrato.id, usuario_email=admin.email,
        detalhes=f"destino={cliente.email}",
    )

    return ContratoEnviarResponse(
        enviado=True,
        destino=cliente.email,
        contrato=contrato,
        detalhe=f"Contrato {contrato.numero} enviado para {cliente.email}.",
    )


@router.get("/{contrato_id}/download")
def baixar_contrato(
    contrato_id: int,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrato não encontrado")

    caminho_absoluto = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", contrato.arquivo_pdf_path)
    )
    if not os.path.isfile(caminho_absoluto):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo do contrato não encontrado em disco")

    return FileResponse(
        caminho_absoluto,
        media_type="application/pdf",
        filename=f"{contrato.numero}.pdf",
    )
