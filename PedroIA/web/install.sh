#!/usr/bin/env bash
# ======================================================================
# PedroIA Web — instalador automático
# Uso:  bash install.sh
# Instala dependências e sobe o ambiente de desenvolvimento.
# ======================================================================
set -e

echo "🚀 PedroIA Web — instalação"

# 1) Verifica Node
if ! command -v node >/dev/null 2>&1; then
  echo "⚠️  Node.js não encontrado."
  echo "    Instale a versão LTS em https://nodejs.org (recomendado: nvm)."
  echo "    Ex.: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash"
  echo "         nvm install --lts"
  exit 1
fi

NODE_MAJOR="$(node -v | sed 's/v\([0-9]*\).*/\1/')"
if [ "$NODE_MAJOR" -lt 18 ]; then
  echo "⚠️  Node $(node -v) detectado. O Next.js precisa de Node 18+."
  exit 1
fi
echo "✅ Node $(node -v)"

# 2) Instala dependências
echo "📦 Instalando dependências..."
if command -v npm >/dev/null 2>&1; then
  npm install
else
  echo "⚠️  npm não encontrado."; exit 1
fi

# 3) Sobe o ambiente
echo "✅ Tudo pronto! Subindo o servidor de desenvolvimento em http://localhost:3000"
npm run dev
