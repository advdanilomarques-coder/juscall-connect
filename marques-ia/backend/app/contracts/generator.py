# -*- coding: utf-8 -*-
"""
Gera o PDF do contrato a partir dos dados reais de um caso e de seu cliente,
usando os modelos de texto definidos em app/contracts/templates.py.

O contrato nasce sempre em status "rascunho" — o envio ao cliente só deve
acontecer depois de aprovação humana (ver app/api/routes_contracts.py).
"""
import os
from datetime import datetime, timezone

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

from app.contracts.templates import TEMPLATES

STORAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "storage", "contratos")

# Dados do escritório usados no cabeçalho e nos contratos.
NOME_ESCRITORIO = "Marques Advogados Associados"
CIDADE_PADRAO = "São Paulo/SP"  # troque pela comarca do escritório, se desejar.

_MESES = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]


def _data_por_extenso() -> str:
    hoje = datetime.now(timezone.utc)
    return f"{hoje.day} de {_MESES[hoje.month - 1]} de {hoje.year}"


def _garantir_diretorio() -> None:
    os.makedirs(os.path.abspath(STORAGE_DIR), exist_ok=True)


def gerar_numero_contrato(contrato_id: int) -> str:
    ano = datetime.now(timezone.utc).year
    return f"MIA-{ano}-{contrato_id:05d}"


def gerar_pdf_contrato(
    contrato_id: int,
    tipo: str,
    nome_cliente: str,
    numero_caso: int,
    resumo_caso: str,
) -> str:
    """
    Gera o arquivo PDF do contrato e retorna o caminho relativo salvo em disco.
    Levanta ValueError se o tipo de contrato não existir nos templates.
    """
    if tipo not in TEMPLATES:
        raise ValueError(f"Tipo de contrato desconhecido: {tipo}")

    _garantir_diretorio()

    template = TEMPLATES[tipo]
    numero = gerar_numero_contrato(contrato_id)
    nome_arquivo = f"{numero}.pdf"
    caminho_completo = os.path.abspath(os.path.join(STORAGE_DIR, nome_arquivo))

    corpo_preenchido = template["corpo"].format(
        nome_cliente=nome_cliente or "Cliente não identificado",
        numero_caso=numero_caso,
        resumo_caso=resumo_caso or "não informado",
        data_extenso=_data_por_extenso(),
        cidade=CIDADE_PADRAO,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="CorpoContrato", fontName="Helvetica", fontSize=10.5,
        leading=16, alignment=TA_JUSTIFY, spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name="TituloContrato", fontName="Helvetica-Bold", fontSize=14,
        leading=18, spaceAfter=18,
    ))
    styles.add(ParagraphStyle(
        name="Escritorio", fontName="Helvetica-Bold", fontSize=15,
        leading=18, alignment=TA_CENTER, spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name="EscritorioSub", fontName="Helvetica", fontSize=9,
        leading=12, alignment=TA_CENTER, textColor="#666666", spaceAfter=16,
    ))
    styles.add(ParagraphStyle(
        name="Assinatura", fontName="Helvetica", fontSize=10,
        leading=14, alignment=TA_CENTER,
    ))

    doc = SimpleDocTemplate(
        caminho_completo, pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2.5*cm, topMargin=2.5*cm, bottomMargin=2.5*cm,
        title=template["titulo"],
    )

    story = [
        Paragraph(NOME_ESCRITORIO, styles["Escritorio"]),
        Paragraph("Advocacia — Direito Bancário e Cível", styles["EscritorioSub"]),
        Paragraph(template["titulo"], styles["TituloContrato"]),
        Paragraph(f"Contrato nº {numero}", styles["Normal"]),
        Spacer(1, 16),
    ]

    for paragrafo in corpo_preenchido.split("\n\n"):
        story.append(Paragraph(paragrafo.replace("\n", "<br/>"), styles["CorpoContrato"]))

    # Campos de assinatura.
    story.append(Spacer(1, 44))
    story.append(Paragraph("_______________________________________", styles["Assinatura"]))
    story.append(Paragraph(f"{nome_cliente or 'CONTRATANTE'}<br/>CONTRATANTE", styles["Assinatura"]))
    story.append(Spacer(1, 28))
    story.append(Paragraph("_______________________________________", styles["Assinatura"]))
    story.append(Paragraph(f"{NOME_ESCRITORIO}<br/>CONTRATADO", styles["Assinatura"]))

    story.append(Spacer(1, 30))
    story.append(Paragraph(
        "Documento gerado automaticamente e sujeito a revisão e aprovação do advogado "
        "responsável antes de qualquer envio ao cliente.",
        styles["EscritorioSub"],
    ))

    doc.build(story)

    # Caminho relativo salvo no banco (mais portável entre ambientes).
    return os.path.join("storage", "contratos", nome_arquivo)
