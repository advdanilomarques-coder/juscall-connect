"""Teste da geração de contratos em PDF.

Verifica que o gerador preenche o modelo e produz um arquivo PDF válido no
disco (checando a assinatura de arquivo '%PDF').
"""

from __future__ import annotations

from app.contracts.generator import generate_pdf


def test_gera_pdf_de_contrato(tmp_path, monkeypatch) -> None:
    # Redireciona o armazenamento para uma pasta temporária do teste.
    from app.core.config import settings

    monkeypatch.setattr(settings, "storage_dir", str(tmp_path))

    path = generate_pdf(
        "honorarios",
        {
            "nome": "João da Silva",
            "cpf": "123.456.789-00",
            "objeto": "Ação revisional de contrato bancário",
            "honorarios": "20% sobre o proveito econômico",
        },
        lead_id=1,
    )

    # O arquivo existe e começa com a assinatura de um PDF.
    with open(path, "rb") as fh:
        assert fh.read(4) == b"%PDF"
