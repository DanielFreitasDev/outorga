"""Monta a página final: injeta o JSON de dados no template (escapando '</' para não fechar o <script>)."""
import json, sys
from pathlib import Path
S = Path(__file__).resolve().parents[1] / "docs" / "demo"
tpl = (S / "template.html").read_text(encoding="utf-8")
dados = Path(sys.argv[1]).read_text(encoding="utf-8")
json.loads(dados)  # valida
html = tpl.replace("__DADOS__", dados.replace("</", "<\\/"))
destino = S / "outorga.html"
destino.write_text(html, encoding="utf-8")
print(destino, len(html) // 1024, "KB")
