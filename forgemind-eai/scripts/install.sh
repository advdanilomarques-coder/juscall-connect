#!/usr/bin/env bash
# ForgeMind EAI — instalacao. Detecta ambiente, valida Node/npm e compila.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "◆ ForgeMind — instalacao"
echo "  SO: $(uname -s) / arquitetura: $(uname -m)"

NODE_MAJOR="$(node -v 2>/dev/null | sed 's/v\([0-9]*\).*/\1/' || echo 0)"
if [ "$NODE_MAJOR" -lt 20 ]; then
  echo "✘ Node 20+ necessario (encontrado: $(node -v 2>/dev/null || echo 'ausente'))." >&2
  exit 1
fi
echo "  Node $(node -v) / npm $(npm -v) — ok"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "  criado .env a partir de .env.example"
fi

echo "  instalando dependencias (precisa de internet uma vez)..."
npm install

echo "  compilando nucleo, servidor e CLI..."
npm run build

echo "  compilando o site..."
npm run build:web

echo ""
echo "✔ Instalado. Proximos passos:"
echo "    ./scripts/start.sh          # sobe o site local"
echo "    node packages/cli/dist/index.js   # abre o chat no terminal"
echo "    ./scripts/model-pull.sh     # (opcional) baixa o cerebro local"
