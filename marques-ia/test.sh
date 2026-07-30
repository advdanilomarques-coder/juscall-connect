#!/bin/bash
# ============================================================
# Marques IA - Executa a suite de testes automatizados
# ============================================================
set -e

if [ ! -d .venv ]; then
  echo "Ambiente virtual nao encontrado. Rode ./install-all.sh primeiro."
  exit 1
fi

source .venv/bin/activate
pip install -r backend/requirements-dev.txt --quiet

echo "Rodando testes..."
cd backend && python3 -m pytest tests/ -v
