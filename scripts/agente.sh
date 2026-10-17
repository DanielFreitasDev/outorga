#!/usr/bin/env bash
# Modo agente: vigia uma pasta e verifica sozinho cada pedido de ATPV-e que chega (IA local, nada sai da máquina).
#   ENTRADA=/srv/outorga/entrada SAIDA=/srv/outorga/saida ./scripts/agente.sh
# Cada pedido = uma subpasta (ou .zip) com a ATPV-e + documentos das empresas (+ pedido.json opcional).
set -euo pipefail
cd "$(dirname "$0")/.."
URL="${OUTORGA_LLM_URL:-http://127.0.0.1:8089/v1}"
if [[ "${OUTORGA_LLM:-llamacpp}" == "llamacpp" ]] && ! curl -sf "${URL%/v1}/health" >/dev/null 2>&1; then
  if command -v qwen-server >/dev/null 2>&1; then
    echo "Subindo o Qwen local..."
    qwen-server
  else
    echo "AVISO: nenhum servidor de IA em $URL — os pedidos ficam na fila até ele subir." >&2
  fi
fi
uv sync --quiet
exec uv run outorga agente ${ENTRADA:+--entrada "$ENTRADA"} ${SAIDA:+--saida "$SAIDA"} ${POLITICA:+--politica "$POLITICA"} "$@"
