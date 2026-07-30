#!/bin/bash
# ============================================================
# Marques IA - Backup do banco de dados e dos contratos gerados
# Roda a partir da raiz do projeto (onde está o .env).
# ============================================================
set -e

if [ ! -f .env ]; then
  echo "Arquivo .env nao encontrado. Rode este script a partir da raiz do projeto."
  exit 1
fi

export $(grep -v '^#' .env | xargs)

DATA=$(date +%Y%m%d_%H%M%S)
DIR_BACKUP="backups/$DATA"
mkdir -p "$DIR_BACKUP"

echo "Gerando dump do banco de dados PostgreSQL..."
docker compose -f docker/docker-compose.yml exec -T db \
  pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$DIR_BACKUP/banco.sql"

echo "Copiando contratos gerados..."
if [ -d backend/storage/contratos ]; then
  cp -r backend/storage/contratos "$DIR_BACKUP/contratos"
else
  echo "Nenhum contrato gerado ainda — pasta storage/contratos vazia."
fi

echo "Backup concluido em: $DIR_BACKUP"
