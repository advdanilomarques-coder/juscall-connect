# -*- coding: utf-8 -*-
"""adiciona coluna email em clientes (envio de contratos/notificações por e-mail)

Revision ID: 0003_cliente_email
Revises: 0002_documentos_rag
Create Date: 2026-07-30

"""
from alembic import op
import sqlalchemy as sa

revision = "0003_cliente_email"
down_revision = "0002_documentos_rag"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("clientes", sa.Column("email", sa.String(length=180), nullable=True))


def downgrade() -> None:
    op.drop_column("clientes", "email")
