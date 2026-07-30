# -*- coding: utf-8 -*-
"""documentos (ocr) e base_conhecimento (rag)

Revision ID: 0002_documentos_rag
Revises: 0001_initial
Create Date: 2026-07-29

"""
from alembic import op
import sqlalchemy as sa

revision = "0002_documentos_rag"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "documentos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("caso_id", sa.Integer(), sa.ForeignKey("casos.id"), nullable=False),
        sa.Column("nome_arquivo", sa.String(length=255), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("caminho_arquivo", sa.String(length=255), nullable=False),
        sa.Column("texto_ocr", sa.Text(), nullable=True),
        sa.Column("confianca_ocr", sa.Float(), nullable=True),
        sa.Column("upload_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_documentos_caso_id", "documentos", ["caso_id"])

    op.create_table(
        "base_conhecimento",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("area_juridica", sa.String(length=40), nullable=False),
        sa.Column("titulo", sa.String(length=200), nullable=False),
        sa.Column("conteudo", sa.Text(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_base_conhecimento_area_juridica", "base_conhecimento", ["area_juridica"])


def downgrade() -> None:
    op.drop_table("base_conhecimento")
    op.drop_table("documentos")
