# -*- coding: utf-8 -*-
"""
Extração de texto de documentos via OCR (Tesseract), usada tanto para
imagens (foto de documento) quanto para PDFs digitalizados (convertidos
página a página em imagem antes do OCR).

Requer o binário do Tesseract instalado no sistema:
  - macOS:  brew install tesseract tesseract-lang
  - Linux:  sudo apt-get install tesseract-ocr tesseract-ocr-por
"""
import logging
from typing import Tuple

import pytesseract
from PIL import Image

logger = logging.getLogger("marques_ia.ocr")

IDIOMA_OCR = "por"

# Abaixo deste percentual de confiança média, o documento é sinalizado
# para revisão manual em vez de ser usado automaticamente.
LIMIAR_CONFIANCA_BAIXA = 60.0


def _confianca_media(dados_ocr: dict) -> float:
    confiancas = [int(c) for c in dados_ocr.get("conf", []) if str(c) not in ("-1", "")]
    return sum(confiancas) / len(confiancas) if confiancas else 0.0


def extrair_texto_imagem(caminho_arquivo: str) -> Tuple[str, float]:
    """Extrai texto e confiança média de uma imagem (PNG/JPG)."""
    imagem = Image.open(caminho_arquivo)
    texto = pytesseract.image_to_string(imagem, lang=IDIOMA_OCR)
    dados = pytesseract.image_to_data(imagem, lang=IDIOMA_OCR, output_type=pytesseract.Output.DICT)
    return texto.strip(), _confianca_media(dados)


def extrair_texto_pdf(caminho_arquivo: str) -> Tuple[str, float]:
    """Extrai texto e confiança média de um PDF digitalizado, página a página."""
    from pdf2image import convert_from_path  # import local: evita custo se não usado

    paginas = convert_from_path(caminho_arquivo)
    textos = []
    todas_confiancas = []

    for pagina in paginas:
        textos.append(pytesseract.image_to_string(pagina, lang=IDIOMA_OCR))
        dados = pytesseract.image_to_data(pagina, lang=IDIOMA_OCR, output_type=pytesseract.Output.DICT)
        confiancas = [int(c) for c in dados.get("conf", []) if str(c) not in ("-1", "")]
        todas_confiancas.extend(confiancas)

    texto_completo = "\n\n".join(t.strip() for t in textos).strip()
    confianca_media = sum(todas_confiancas) / len(todas_confiancas) if todas_confiancas else 0.0
    return texto_completo, confianca_media


def processar_documento(caminho_arquivo: str, tipo: str) -> Tuple[str, float]:
    """
    Ponto de entrada único do módulo: recebe o caminho do arquivo salvo em
    disco e o tipo ("pdf" ou "image"), e retorna (texto_extraido, confianca_media).
    """
    try:
        if tipo == "pdf":
            return extrair_texto_pdf(caminho_arquivo)
        return extrair_texto_imagem(caminho_arquivo)
    except Exception as exc:  # noqa: BLE001 — OCR não deve derrubar o upload
        logger.error("Falha ao processar OCR de %s: %s", caminho_arquivo, exc)
        return "", 0.0
