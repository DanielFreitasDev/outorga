"""Gera docs/Outorga-apresentacao.pdf a partir de docs/apresentacao/apresentacao.html (WeasyPrint).

As imagens ficam em docs/apresentacao/img/ (telas do app em tema claro, com dados fictícios).

    uv run python scripts/gerar_apresentacao.py
"""

from pathlib import Path

from weasyprint import HTML

RAIZ = Path(__file__).resolve().parents[1]
ORIGEM = RAIZ / "docs" / "apresentacao" / "apresentacao.html"
DESTINO = RAIZ / "docs" / "Outorga-apresentacao.pdf"

if __name__ == "__main__":
    HTML(filename=str(ORIGEM)).write_pdf(str(DESTINO))
    print(DESTINO)
