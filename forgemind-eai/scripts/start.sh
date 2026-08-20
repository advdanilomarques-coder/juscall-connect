#!/usr/bin/env bash
# Sobe o backend local do ForgeMind (site + API). Nunca hospeda publicamente.
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] && export $(grep -v '^#' .env | grep -v '^$' | xargs) || true

if [ ! -f packages/server/dist/index.js ]; then
  echo "servidor nao compilado — rodando build..."
  npm run build
fi

# Garante o site compilado, senao a raiz "/" daria 404.
if [ ! -f packages/web/dist/index.html ]; then
  echo "site nao compilado — rodando build:web..."
  npm run build:web
fi

HOST="${FORGEMIND_HOST:-127.0.0.1}"
PORT="${FORGEMIND_PORT:-4319}"
echo "◆ ForgeMind subindo em http://$HOST:$PORT"
exec node packages/server/dist/index.js
