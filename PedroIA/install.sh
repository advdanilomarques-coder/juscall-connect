#!/usr/bin/env bash
#
# PedroIA — instalador automático
# Uso:  bash install.sh
#
# O script:
#   - verifica dependências (python3, node, npm)
#   - cria o ambiente virtual do backend e instala as libs
#   - prepara o arquivo .env (a partir de .env.example)
#   - inicializa o banco de dados (SQLite por padrão)
#   - compila e empacota a extensão do VS Code
#   - instala a extensão no VS Code (se o comando `code` estiver disponível)
#
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# ---------- helpers ----------
BLUE='\033[0;34m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${BLUE}▶${NC} $*"; }
ok()    { echo -e "${GREEN}✔${NC} $*"; }
warn()  { echo -e "${YELLOW}!${NC} $*"; }
err()   { echo -e "${RED}x${NC} $*" >&2; }

need() {
  if ! command -v "$1" >/dev/null 2>&1; then
    err "Dependência ausente: '$1'. Instale antes de continuar."
    return 1
  fi
}

echo -e "${BLUE}"
echo "  ____           _           ___    _    "
echo " |  _ \ ___  __| |_ __ ___ |_ _|  / \   "
echo " | |_) / _ \/ _\` | '__/ _ \ | |  / _ \  "
echo " |  __/  __/ (_| | | | (_) || | / ___ \ "
echo " |_|   \___|\__,_|_|  \___/|___/_/   \_\\"
echo -e "${NC}"
echo " Seu engenheiro de IA dentro do VS Code"
echo "-----------------------------------------"

# ---------- 1. dependências ----------
info "Verificando dependências…"
MISSING=0
need python3 || MISSING=1
need node || warn "Node.js não encontrado — a extensão não será compilada."
need npm  || warn "npm não encontrado — a extensão não será compilada."
if [ "$MISSING" -eq 1 ]; then
  err "Instale as dependências obrigatórias e execute novamente."
  exit 1
fi
ok "Dependências principais presentes."

# ---------- 2. backend ----------
info "Configurando o backend (FastAPI)…"
cd "$ROOT_DIR/backend"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  ok "Ambiente virtual criado (.venv)."
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
ok "Dependências Python instaladas."

if [ ! -f ".env" ]; then
  cp .env.example .env
  ok "Arquivo .env criado a partir de .env.example."
else
  warn ".env já existe — mantido."
fi

# Inicializa o schema do banco (cria as tabelas).
python -c "import asyncio; from app.database.session import init_db; asyncio.run(init_db())"
ok "Banco de dados inicializado."
deactivate
cd "$ROOT_DIR"

# ---------- 3. extensão VS Code ----------
if command -v npm >/dev/null 2>&1; then
  info "Compilando a extensão do VS Code…"
  cd "$ROOT_DIR/extension"
  npm install --silent
  node ./esbuild.js --production
  ok "Extensão compilada (dist/extension.js)."

  # Empacota .vsix se o vsce estiver disponível.
  if npx --no-install @vscode/vsce --version >/dev/null 2>&1; then
    npx --no-install @vscode/vsce package --allow-missing-repository -o pedroia.vsix || warn "Falha ao empacotar .vsix (opcional)."
  else
    warn "vsce não instalado — pulei o empacotamento .vsix. (npm i -g @vscode/vsce)"
  fi

  # Instala no VS Code, se possível.
  if command -v code >/dev/null 2>&1 && [ -f "pedroia.vsix" ]; then
    code --install-extension pedroia.vsix && ok "Extensão instalada no VS Code."
  else
    warn "Comando 'code' ou .vsix ausente — instale manualmente com: code --install-extension pedroia.vsix"
  fi
  cd "$ROOT_DIR"
else
  warn "Pulando a extensão (npm ausente)."
fi

# ---------- 4. instruções finais ----------
echo
ok "Instalação concluída!"
echo
echo "Para iniciar o backend:"
echo -e "  ${GREEN}cd backend && source .venv/bin/activate && uvicorn app.main:app --reload${NC}"
echo
echo "Depois abra o VS Code, clique no ícone do PedroIA na barra lateral e comece a conversar."
echo "Documentação da API: http://127.0.0.1:8000/docs"
echo
echo "Dica (modo offline): instale o Ollama e rode 'ollama pull llama3.1'."
