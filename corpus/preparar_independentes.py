"""Converte os casos do autor independente (corpus/independente/<ID>/) em casos executáveis (corpus/casos/<ID>/).

    uv run python corpus/preparar_independentes.py
Markdown → PDF (mesma aparência do corpus) e CRLV simulado a partir de pedido.json (veiculo + crlv_proprietario).
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from weasyprint import HTML

from gerar_casos import CSS_CRLV, md_para_pdf

AQUI = Path(__file__).parent


def crlv_html(pedido: dict) -> str:
    v, dono = pedido["veiculo"], pedido.get("crlv_proprietario") or pedido["vendedor"]
    nome = dono.get("nome") or dono.get("razao_social")
    doc = dono.get("documento") or dono.get("cnpj")
    campos = [("Código RENAVAM", v.get("renavam", "")), ("Placa", v.get("placa", "")), ("Exercício", "2026"),
              ("Marca / Modelo / Versão", v.get("descricao", "")), ("Chassi", v.get("chassi", "")), ("Nome", nome),
              ("CPF / CNPJ", doc), ("Data", "15/01/2026")]
    linhas = "".join(f"<tr><td colspan='3'><span>{k}</span><b>{val}</b></td></tr>" for k, val in campos)
    return (f"<html><head><meta charset='utf-8'><style>{CSS_CRLV}</style></head><body>"
            "<div class='marca'>DOCUMENTO SIMULADO</div><div class='cab'><h1>CERTIFICADO DE REGISTRO E LICENCIAMENTO DE VEÍCULO</h1>"
            "<p>Reprodução simulada para testes de software — sem valor legal</p></div>"
            f"<table>{linhas}</table></body></html>")


def _com_cpfs(esp: dict | None) -> dict | None:
    if not esp:
        return None
    esp = dict(esp)
    esp.setdefault("conjuntos_minimos_cpf", None)
    return esp


def main() -> None:
    n = 0
    for pasta in sorted(p for p in (AQUI / "independente").glob("I*") if p.is_dir()):
        destino = AQUI / "casos" / pasta.name
        if destino.exists():
            shutil.rmtree(destino)
        (destino / "docs").mkdir(parents=True)
        for md in sorted((pasta / "docs").glob("*.md")):
            md_para_pdf(md.read_text(encoding="utf-8"), destino / "docs" / f"{md.stem}.pdf")
        pedido = json.loads((pasta / "pedido.json").read_text(encoding="utf-8"))
        HTML(string=crlv_html(pedido)).write_pdf(destino / "docs" / "CRLV.pdf")
        (destino / "pedido.json").write_text(json.dumps(pedido, ensure_ascii=False, indent=2), encoding="utf-8")
        gab = json.loads((pasta / "gabarito.json").read_text(encoding="utf-8"))
        gab["esperado"] = _com_cpfs(gab["esperado"])
        gab["esperado_ce"] = _com_cpfs(gab.get("esperado_ce"))
        gab.setdefault("validacao_cega", True)
        (destino / "gabarito.json").write_text(json.dumps(gab, ensure_ascii=False, indent=2), encoding="utf-8")
        n += 1
    print(f"{n} casos independentes preparados em {AQUI / 'casos'}")


if __name__ == "__main__":
    main()
