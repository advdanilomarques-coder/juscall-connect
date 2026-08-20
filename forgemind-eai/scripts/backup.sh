#!/usr/bin/env bash
# Backup de memoria/historico (nunca inclui .env, keys ou segredos).
set -euo pipefail
cd "$(dirname "$0")/.."
node packages/cli/dist/index.js backup
