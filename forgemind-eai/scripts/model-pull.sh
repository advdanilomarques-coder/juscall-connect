#!/usr/bin/env bash
# Baixa o cerebro local (GGUF). Uma vez, com internet; depois 100% offline.
# Padrao recomendado p/ Mac Intel ~10GB: Qwen2.5-3B-Instruct Q4_K_M (~2GB).
# Modo rapido (menos RAM): passe "1.5b".
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p models

SIZE="${1:-3b}"
case "$SIZE" in
  3b)
    NAME="qwen2.5-3b-instruct-q4_k_m.gguf"
    URL="https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf"
    ;;
  1.5b)
    NAME="qwen2.5-1.5b-instruct-q4_k_m.gguf"
    URL="https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
    ;;
  *)
    echo "uso: model-pull.sh [3b|1.5b]" >&2; exit 1;;
esac

DEST="models/$NAME"
if [ -f "$DEST" ]; then
  echo "✔ modelo ja existe: $DEST"
else
  echo "◆ baixando $NAME (isso pode demorar)..."
  curl -L --fail -o "$DEST" "$URL"
  echo "✔ salvo em $DEST"
fi

echo ""
echo "Agora ative o cerebro local:"
echo "  1) em .env: AI_PROVIDER=local-llama e LOCAL_MODEL_PATH=./$DEST"
echo "  2) instale o runtime (uma vez): npm install node-llama-cpp --workspace @forgemind/core"
echo "  3) reinicie: ./scripts/start.sh"
echo ""
echo "Ou troque o provider pela pagina /config do seu site."
