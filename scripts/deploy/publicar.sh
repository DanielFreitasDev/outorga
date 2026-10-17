#!/usr/bin/env bash
# Publica (ou atualiza) a demonstração num servidor Linux com systemd, a partir do commit atual.
#   SERVIDOR=usuario@host [CHAVE=~/.ssh/chave] ./scripts/deploy/publicar.sh
# Pré-requisitos no servidor (uma vez): tesseract-ocr tesseract-ocr-por libpango-1.0-0 libpangoft2-1.0-0 fonts-dejavu-core,
# uv em /usr/local/bin, usuário de sistema "outorga", /etc/outorga/outorga.env e o serviço scripts/deploy/outorga-demo.service.
# A exposição na internet é feita por um Cloudflare Tunnel apontando um hostname para http://localhost:54325.
set -euo pipefail
cd "$(dirname "$0")/../.."
: "${SERVIDOR:?defina SERVIDOR=usuario@host}"
SSH=(ssh -o BatchMode=yes ${CHAVE:+-i "$CHAVE"} "$SERVIDOR")
(cd web && pnpm build >/dev/null)
git archive --format=tar HEAD | "${SSH[@]}" 'sudo mkdir -p /opt/outorga && sudo tar -x -C /opt/outorga'
tar -C web -cf - dist | "${SSH[@]}" 'sudo mkdir -p /opt/outorga/web && sudo rm -rf /opt/outorga/web/dist && sudo tar -x -C /opt/outorga/web'
"${SSH[@]}" 'set -e; sudo mkdir -p /opt/outorga/dados; sudo chown -R outorga:outorga /opt/outorga; cd /opt/outorga
  sudo -u outorga env HOME=/opt/outorga UV_CACHE_DIR=/opt/outorga/.uv-cache UV_PYTHON_INSTALL_DIR=/opt/outorga/.python \
    /usr/local/bin/uv sync --frozen --no-dev -q
  sudo systemctl restart outorga
  for i in $(seq 1 30); do curl -sf http://127.0.0.1:54325/api/saude >/dev/null && break; sleep 1; done
  systemctl is-active outorga'
