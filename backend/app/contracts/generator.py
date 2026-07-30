"""Gerador de contratos em PDF (fpdf2).

Recebe um modelo (templates.py) e um dicionário de dados, preenche os
placeholders e exporta um PDF no disco. O caminho do PDF é devolvido para ser
registrado no banco (tabela `contracts`).

fpdf2 é puro-Python (sem dependências de sistema), então funciona em qualquer
ambiente, inclusive local sem Docker.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

from app.contracts.templates import get_template
from app.core.config import settings


def _fill(text: str, data: dict) -> str:
    """Substitui os placeholders {campo} pelos valores; campos ausentes viram '—'."""

    class _Default(dict):
        def __missing__(self, key: str) -> str:  # noqa: D401
            return "—"

    return text.format_map(_Default(data))


def _latin1(text: str) -> str:
    """Torna o texto compatível com a fonte core do fpdf (Latin-1).

    As fontes padrão do fpdf2 não suportam todos os caracteres Unicode; esta
    conversão evita erros de codificação mantendo os acentos do português.
    """
    return text.encode("latin-1", "replace").decode("latin-1")


def generate_pdf(template_name: str, data: dict, *, lead_id: int) -> str:
    """Gera o PDF do contrato e retorna o caminho do arquivo salvo."""
    try:
        from fpdf import FPDF
    except ImportError as exc:
        raise RuntimeError(
            "Biblioteca 'fpdf2' não instalada. Rode: pip install fpdf2"
        ) from exc

    template = get_template(template_name)

    # Preenche campos automáticos que o chamador pode não ter passado.
    data = {
        "data": datetime.now(timezone.utc).strftime("%d/%m/%Y"),
        "cidade": settings.firm_city,
        "advogado": settings.firm_lawyer,
        "oab": settings.firm_oab,
        **data,
    }

    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Cabeçalho com o nome do escritório.
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _latin1(settings.firm_name), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Título do contrato.
    pdf.set_font("Helvetica", "B", 12)
    pdf.multi_cell(0, 8, _latin1(template["titulo"]), align="C")
    pdf.ln(4)

    # Corpo (parágrafos justificados).
    pdf.set_font("Helvetica", "", 11)
    for paragrafo in template["paragrafos"]:
        pdf.multi_cell(0, 7, _latin1(_fill(paragrafo, data)), align="J")
        pdf.ln(2)

    # Assinaturas.
    pdf.ln(10)
    for assinatura in template["assinaturas"]:
        for linha in _fill(assinatura, data).split("\n"):
            pdf.cell(0, 7, _latin1(linha), align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(6)

    # Salva em STORAGE_DIR/contracts/lead_<id>/...
    directory = os.path.join(settings.storage_dir, "contracts", f"lead_{lead_id}")
    os.makedirs(directory, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = os.path.join(directory, f"contrato_{template_name}_{stamp}.pdf")
    pdf.output(path)
    return path
