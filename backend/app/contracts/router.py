"""Rotas de contratos (painel administrativo — protegidas por JWT).

Fluxo de "Gerar Contrato": o admin envia o objeto e os honorários; o sistema
puxa os dados cadastrais do lead, gera o PDF, registra o contrato no banco e
avança o lead no funil para "contrato gerado".
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.generator import generate_pdf
from app.crm.service import CRMService
from app.db.models import Contract, LeadStatus
from app.deps import get_current_admin, get_session

router = APIRouter(
    prefix="/contracts",
    tags=["Contratos"],
    dependencies=[Depends(get_current_admin)],
)


class ContractIn(BaseModel):
    template: str = Field(default="honorarios", description="Nome do modelo.")
    object_text: str = Field(..., description="Objeto do contrato.")
    fees: str = Field(..., description="Honorários acordados.")


class ContractOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    template: str
    object_text: str | None
    fees: str | None
    signed: bool
    created_at: datetime


@router.post("/leads/{lead_id}", response_model=ContractOut, status_code=201)
async def generate_contract(
    lead_id: int,
    data: ContractIn,
    session: AsyncSession = Depends(get_session),
) -> ContractOut:
    """Gera o contrato em PDF preenchido com os dados do lead."""
    crm = CRMService(session)
    lead = await crm.get_lead(lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead não encontrado.")

    pdf_path = generate_pdf(
        data.template,
        {
            "nome": lead.name or "",
            "cpf": lead.cpf or "",
            "rg": lead.rg or "",
            "endereco": lead.address or "",
            "telefone": lead.phone,
            "email": lead.email or "",
            "objeto": data.object_text,
            "honorarios": data.fees,
        },
        lead_id=lead_id,
    )

    contract = Contract(
        lead_id=lead_id,
        template=data.template,
        object_text=data.object_text,
        fees=data.fees,
        pdf_path=pdf_path,
    )
    session.add(contract)

    # Avança o lead no funil.
    lead.status = LeadStatus.CONTRATO_GERADO

    await session.commit()
    await session.refresh(contract)
    return ContractOut.model_validate(contract)


@router.get("/leads/{lead_id}", response_model=list[ContractOut])
async def list_contracts(
    lead_id: int, session: AsyncSession = Depends(get_session)
) -> list[ContractOut]:
    result = await session.execute(
        select(Contract).where(Contract.lead_id == lead_id).order_by(Contract.id.desc())
    )
    return [ContractOut.model_validate(c) for c in result.scalars().all()]


@router.get("/{contract_id}/download")
async def download_contract(
    contract_id: int, session: AsyncSession = Depends(get_session)
) -> FileResponse:
    contract = await session.get(Contract, contract_id)
    if contract is None or not contract.pdf_path:
        raise HTTPException(status_code=404, detail="Contrato não encontrado.")
    return FileResponse(
        contract.pdf_path,
        filename=f"contrato_{contract_id}.pdf",
        media_type="application/pdf",
    )
