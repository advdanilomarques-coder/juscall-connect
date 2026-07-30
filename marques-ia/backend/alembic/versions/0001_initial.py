# -*- coding: utf-8 -*-
"""schema inicial — clientes, casos, mensagens, contratos, admin, auditoria

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-28

"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "clientes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telefone", sa.String(length=20), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("ultimo_contato_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_clientes_telefone", "clientes", ["telefone"], unique=True)

    op.create_table(
        "usuarios_admin",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=180), nullable=False),
        sa.Column("senha_hash", sa.String(length=255), nullable=False),
        sa.Column("papel", sa.String(length=30), server_default="admin"),
        sa.Column("ativo", sa.Boolean(), server_default=sa.true()),
    )
    op.create_index("ix_usuarios_admin_email", "usuarios_admin", ["email"], unique=True)

    op.create_table(
        "casos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cliente_id", sa.Integer(), sa.ForeignKey("clientes.id"), nullable=False),
        sa.Column("area_juridica", sa.String(length=40), server_default="outro"),
        sa.Column("etapa_funil", sa.String(length=30), server_default="novo_lead"),
        sa.Column("status", sa.String(length=20), server_default="aberto"),
        sa.Column("responsavel", sa.String(length=120), nullable=True),
        sa.Column("resumo", sa.Text(), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_casos_cliente_id", "casos", ["cliente_id"])
    op.create_index("ix_casos_etapa_funil", "casos", ["etapa_funil"])

    op.create_table(
        "mensagens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cliente_id", sa.Integer(), sa.ForeignKey("clientes.id"), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("conteudo", sa.Text(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_mensagens_cliente_id", "mensagens", ["cliente_id"])

    op.create_table(
        "contratos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("caso_id", sa.Integer(), sa.ForeignKey("casos.id"), nullable=False),
        sa.Column("tipo", sa.String(length=60), nullable=False),
        sa.Column("arquivo_pdf_path", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="rascunho"),
        sa.Column("numero", sa.String(length=40), nullable=True),
        sa.Column("gerado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_contratos_caso_id", "contratos", ["caso_id"])
    op.create_index("ix_contratos_numero", "contratos", ["numero"], unique=True)

    op.create_table(
        "logs_auditoria",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("usuario_email", sa.String(length=180), nullable=True),
        sa.Column("acao", sa.String(length=60), nullable=False),
        sa.Column("entidade", sa.String(length=60), nullable=False),
        sa.Column("entidade_id", sa.Integer(), nullable=True),
        sa.Column("detalhes", sa.Text(), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_logs_auditoria_acao", "logs_auditoria", ["acao"])
    op.create_index("ix_logs_auditoria_entidade", "logs_auditoria", ["entidade"])


def downgrade() -> None:
    op.drop_table("logs_auditoria")
    op.drop_table("contratos")
    op.drop_table("mensagens")
    op.drop_table("casos")
    op.drop_table("usuarios_admin")
    op.drop_table("clientes")
