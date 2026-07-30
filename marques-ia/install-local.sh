#!/bin/bash
# ============================================================
# Marques IA - Instalacao LOCAL, SEM DOCKER (usa SQLite)
# Ideal para rodar/testar no seu computador sem instalar
# PostgreSQL, Redis ou Docker. Le APENAS o arquivo .env.
#
# Diferenca para o install-all.sh:
#   - NAO usa Docker (nem Postgres, nem Redis)
#   - O banco de dados vira um unico arquivo: marques_ia.db (SQLite)
#   - Todo o resto (login, painel, IA, WhatsApp, contratos, e-mail) e igual
# ============================================================
set -e

echo "=========================================="
echo " Marques IA - Instalacao LOCAL (sem Docker)"
echo "=========================================="

# 1. Verifica se o .env existe
if [ ! -f .env ]; then
  echo "Arquivo .env nao encontrado."
  echo "Copie .env.example para .env e preencha os valores antes de continuar."
  exit 1
fi

# 2. Confere se a chave da OpenRouter foi preenchida (unica obrigatoria)
CHAVE=$(grep -E '^OPENROUTER_API_KEY=' .env | cut -d '=' -f2-)
if [ -z "$CHAVE" ] || [ "$CHAVE" = "coloque_aqui_sua_unica_chave_gratuita" ] || [ "$CHAVE" = "COLE_AQUI_SUA_CHAVE_sk-or-v1" ]; then
  echo "OPENROUTER_API_KEY nao preenchida no .env."
  echo "Abra o .env, cole sua chave (sk-or-v1-...) e rode de novo."
  exit 1
fi

# 3. Forca o uso de SQLite (arquivo local, caminho absoluto para evitar
#    confusao de diretorio entre os scripts e o uvicorn).
export DATABASE_URL="sqlite:///$(pwd)/marques_ia.db"
echo "Banco de dados: SQLite em $(pwd)/marques_ia.db"

echo "[1/6] Criando ambiente virtual Python..."
python3 -m venv .venv
source .venv/bin/activate

echo "[2/6] Instalando dependencias do backend..."
pip install --upgrade pip --quiet
pip install -r backend/requirements.txt --quiet

echo "[3/6] Criando as tabelas e o usuario administrador padrao..."
python3 backend/scripts/create_admin.py

echo "[4/6] Populando a base de conhecimento inicial (RAG)..."
python3 backend/scripts/seed_knowledge.py

echo "[5/6] Validando OPENROUTER_API_KEY e os modelos gratuitos configurados..."
python3 backend/scripts/check_ai_provider.py

echo "[6/6] Iniciando aplicacao..."
echo "-------------------------------------------------------"
echo "Painel/API disponivel em: http://localhost:8000/painel"
echo "Login padrao: veja ADMIN_DEFAULT_EMAIL / ADMIN_DEFAULT_PASSWORD no seu .env"
echo "-------------------------------------------------------"

cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
