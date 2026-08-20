#!/usr/bin/env bash
# Para o backend local do ForgeMind (por porta).
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] && export $(grep -v '^#' .env | grep -v '^$' | xargs) || true
PORT="${FORGEMIND_PORT:-4319}"

PIDS="$(lsof -ti tcp:"$PORT" 2>/dev/null || true)"
if [ -z "$PIDS" ]; then
  echo "ForgeMind nao esta rodando na porta $PORT."
  exit 0
fi
echo "parando ForgeMind (pids: $PIDS)"
kill $PIDS 2>/dev/null || true
echo "✔ parado."
