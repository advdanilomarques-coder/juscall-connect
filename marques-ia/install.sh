#!/bin/bash
# ============================================================
# Marques IA - Instalador rapido (SEM Docker, usa SQLite)
#
# Faz tudo em um comando:
#   - cria o ambiente virtual e instala as dependencias (pips)
#   - usa SQLite (um arquivo local, sem Postgres/Redis/Docker)
#   - seleciona automaticamente modelos gratuitos que FUNCIONAM na OpenRouter
#   - cria as pastas, o banco, o usuario admin e a base de conhecimento
#   - valida a chave de IA e inicia o servidor
#
# Uso:
#   cd marques-ia
#   chmod +x install.sh
#   ./install.sh
# ============================================================
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "=========================================="
echo " Marques IA - Instalador rapido (sem Docker)"
echo "=========================================="

# 1. .env
if [ ! -f .env ]; then
  echo "ERRO: arquivo .env nao encontrado."
  echo "Copie .env.example para .env e preencha a OPENROUTER_API_KEY."
  exit 1
fi

CHAVE=$(grep -E '^OPENROUTER_API_KEY=' .env | cut -d= -f2-)
if [ -z "$CHAVE" ] || [ "$CHAVE" = "coloque_aqui_sua_unica_chave_gratuita" ] || [ "$CHAVE" = "COLE_SUA_CHAVE_AQUI" ]; then
  echo "ERRO: OPENROUTER_API_KEY nao preenchida no .env."
  echo "Cole sua chave (sk-or-v1-...) no .env e rode novamente."
  exit 1
fi

# 2. Forca SQLite (caminho absoluto, evita confusao de diretorio)
export DATABASE_URL="sqlite:///$DIR/marques_ia.db"
echo "Banco: SQLite em $DIR/marques_ia.db"

# 3. Ambiente virtual + dependencias
echo "[1/6] Criando ambiente virtual Python..."
python3 -m venv .venv
source .venv/bin/activate

echo "[2/6] Instalando dependencias (pips)..."
pip install --upgrade pip --quiet
pip install -r backend/requirements.txt --quiet

# 4. Seleciona modelos gratuitos que existem AGORA na OpenRouter
echo "[3/6] Selecionando modelos gratuitos disponiveis..."
python3 - <<'PY' || echo "  (aviso: nao foi possivel atualizar os modelos automaticamente; seguindo com os do .env)"
import re, httpx
key = None
for line in open('.env'):
    if line.startswith('OPENROUTER_API_KEY='):
        key = line.split('=', 1)[1].strip()
r = httpx.get('https://openrouter.ai/api/v1/models',
              headers={'Authorization': f'Bearer {key}'}, timeout=30)
free = [m['id'] for m in r.json()['data'] if m['id'].endswith(':free')]
pref = [m for m in free if re.search(r'instruct|chat|-it', m)]
escolha = (pref or free)[:3]
if not escolha:
    raise SystemExit('nenhum modelo :free encontrado')
print('  Modelos escolhidos:', escolha)
keep = [l for l in open('.env')
        if not l.startswith(('OPENROUTER_MODEL_PRIMARY',
                             'OPENROUTER_MODEL_FALLBACK_1',
                             'OPENROUTER_MODEL_FALLBACK_2'))]
keep.append(f'OPENROUTER_MODEL_PRIMARY={escolha[0]}\n')
if len(escolha) > 1: keep.append(f'OPENROUTER_MODEL_FALLBACK_1={escolha[1]}\n')
if len(escolha) > 2: keep.append(f'OPENROUTER_MODEL_FALLBACK_2={escolha[2]}\n')
open('.env', 'w').writelines(keep)
PY

# 5. Banco, pastas, admin e base de conhecimento
echo "[4/6] Criando pastas, banco e usuario administrador..."
mkdir -p backend/storage/contratos backend/storage/documentos
python3 backend/scripts/create_admin.py
python3 backend/scripts/seed_knowledge.py

# 6. Valida a chave/modelos
echo "[5/6] Validando a chave de IA e os modelos..."
python3 backend/scripts/check_ai_provider.py

# 7. Inicia
echo "[6/6] Iniciando o servidor..."
echo "-------------------------------------------------------"
echo "Painel:  http://localhost:8000/painel"
echo "Login:   veja ADMIN_DEFAULT_EMAIL / ADMIN_DEFAULT_PASSWORD no .env"
echo "Deixe esta janela aberta (ela roda o servidor)."
echo "-------------------------------------------------------"

uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir backend
