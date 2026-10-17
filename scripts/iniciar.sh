#!/usr/bin/env bash
# Sobe o LLM local (se preciso) e a API + interface do Outorga em http://127.0.0.1:${PORTA:-8765}
set -euo pipefail
cd "$(dirname "$0")/.."
URL="${OUTORGA_LLM_URL:-http://127.0.0.1:8089/v1}"
if [[ "${OUTORGA_LLM:-llamacpp}" == "llamacpp" ]] && ! curl -sf "${URL%/v1}/health" >/dev/null 2>&1; then
  if command -v qwen-server >/dev/null 2>&1; then
    echo "Subindo o Qwen local (o perfil 'coexist' é escolhido sozinho se o whisper estiver ativo)..."
    qwen-server
  else
    echo "AVISO: nenhum servidor LLM em $URL — a demonstração pré-calculada funciona, a leitura ao vivo não." >&2
  fi
fi
if [[ ! -f web/dist/index.html ]]; then
  (cd web && pnpm install --frozen-lockfile && pnpm build)
fi
uv sync --quiet
exec uv run outorga serve --porta "${PORTA:-8765}"
