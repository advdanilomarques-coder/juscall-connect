#!/usr/bin/env bash
# ============================================================================
# SCRIPT DE PREPARAÇÃO DO AMBIENTE — MARQUES IA (Backend)
# ----------------------------------------------------------------------------
# Automatiza os passos manuais: cria o ambiente virtual, instala as
# dependências e prepara o arquivo .env.
#
# Uso:
#   cd backend
#   bash setup.sh
# ============================================================================
set -euo pipefail

echo "==> 1/4 Criando ambiente virtual (.venv)..."
python3 -m venv .venv

echo "==> 2/4 Ativando ambiente virtual..."
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> 3/4 Instalando dependências (requirements.txt)..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> 4/4 Preparando arquivo .env..."
if [ ! -f .env ]; then
  cp .env.example .env
  echo "    .env criado a partir de .env.example — preencha suas chaves de API."
else
  echo "    .env já existe — mantido."
fi

echo ""
echo "Ambiente pronto! Próximos passos:"
echo "  1) Edite o arquivo .env e coloque sua ANTHROPIC_API_KEY."
echo "  2) source .venv/bin/activate"
echo "  3) uvicorn app.main:app --reload"
