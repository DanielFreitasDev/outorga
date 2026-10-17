#!/usr/bin/env bash
# Baixa os dados de português do Tesseract para vendor/tessdata (alternativa ao pacote do sistema tesseract-ocr-por).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p vendor/tessdata
for idioma in por osd; do
  curl -fsSL -o "vendor/tessdata/$idioma.traineddata" \
    "https://github.com/tesseract-ocr/tessdata_fast/raw/main/$idioma.traineddata"
done
echo "ok: $(ls vendor/tessdata)"
