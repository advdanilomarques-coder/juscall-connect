#!/bin/bash
# ============================================================
# Marques IA - Instalacao e execucao (Backend + Agente de IA)
# Le APENAS o arquivo .env. Nenhum outro arquivo precisa ser editado.
# ============================================================
set -e

echo "=========================================="
echo " Marques IA - Instalacao (Backend + IA)"
echo "=========================================="

# 1. Verifica se o .env existe
if [ ! -f .env ]; then
  echo "Arquivo .env nao encontrado."
  echo "Copie .env.example para .env e preencha os valores antes de continuar."
  exit 1
fi

# 2. Carrega as variaveis do .env
export $(grep -v '^#' .env | xargs)

if [ -z "$OPENROUTER_API_KEY" ] || [ "$OPENROUTER_API_KEY" = "coloque_aqui_sua_unica_chave_gratuita" ]; then
  echo "OPENROUTER_API_KEY nao preenchida no .env. Preencha e execute novamente."
  exit 1
fi

echo "[1/8] Criando ambiente virtual Python..."
python3 -m venv .venv
source .venv/bin/activate

echo "[2/8] Instalando dependencias do backend..."
pip install --upgrade pip --quiet
pip install -r backend/requirements.txt --quiet

echo "[3/8] Subindo banco de dados e Redis via Docker..."
docker compose -f docker/docker-compose.yml up -d db redis

echo "[4/8] Aguardando banco de dados ficar disponivel..."
until docker compose -f docker/docker-compose.yml exec -T db pg_isready -U "$POSTGRES_USER" > /dev/null 2>&1; do
  sleep 2
done

echo "[5/8] Aplicando migracoes do banco (Alembic)..."
cd backend && alembic upgrade head && cd ..

echo "[6/8] Criando usuario administrador padrao (se nao existir)..."
python3 backend/scripts/create_admin.py

echo "[6b/8] Populando a base de conhecimento inicial (RAG)..."
python3 backend/scripts/seed_knowledge.py

echo "[7/8] Validando OPENROUTER_API_KEY e os modelos gratuitos configurados..."
python3 backend/scripts/check_ai_provider.py

echo "[8/8] Iniciando aplicacao..."
echo "Numero WhatsApp configurado: $WHATSAPP_PHONE_NUMBER"
echo "Login padrao do painel: $ADMIN_DEFAULT_EMAIL"
echo "Painel/API disponivel em: http://localhost:8000"

cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
