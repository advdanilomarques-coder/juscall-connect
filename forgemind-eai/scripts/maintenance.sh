#!/usr/bin/env bash
# Manutencao / self-healing seguro (PDF item 38-40).
# Uso: maintenance.sh [--diagnose|--repair]
set -euo pipefail
cd "$(dirname "$0")/.."

MODE="${1:---diagnose}"
echo "◆ ForgeMind manutencao ($MODE)"

case "$MODE" in
  --diagnose)
    node packages/cli/dist/index.js doctor || true
    ;;
  --repair)
    echo "  verificando build..."
    [ -f packages/server/dist/index.js ] || npm run build
    echo "  validando banco SQLite..."
    node packages/cli/dist/index.js doctor || true
    echo "  limpando caches seguros (dist de web mantido)..."
    find . -name "*.tsbuildinfo" -delete 2>/dev/null || true
    echo "✔ reparo seguro concluido. Nenhum dado foi apagado."
    ;;
  *)
    echo "uso: maintenance.sh [--diagnose|--repair]" >&2
    exit 1
    ;;
esac
