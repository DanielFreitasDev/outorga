"""Monta os casos de avaliação a partir da especificação e dos documentos redigidos.

Para cada caso cria `corpus/casos/<ID>/` com:
  docs/*.pdf      documentos do caso (PDF com aparência de documento; CRLV simulado)
  pedido.json     o pedido de venda (veículo, data, valor, assinantes como digitados)
  gabarito.json   o resultado esperado
O caso marcado com `ocr: true` recebe os PDFs rasterizados (simulando digitalização).

Todo PDF leva no rodapé: "CORPUS SINTÉTICO — DADOS FICTÍCIOS — SEM VALOR LEGAL".

    uv run python corpus/gerar_casos.py
"""

from __future__ import annotations

import io
import json
import random
import shutil
from pathlib import Path

import fitz  # PyMuPDF
import markdown
from PIL import Image, ImageFilter
from weasyprint import HTML

AQUI = Path(__file__).parent
SPEC = json.loads((AQUI / "cenarios.json").read_text(encoding="utf-8"))
PDF_DIR = AQUI / "pdf"
CASOS_DIR = AQUI / "casos"
AVISO = "CORPUS SINTÉTICO OUTORGA — DADOS FICTÍCIOS — SEM VALOR LEGAL"

CSS = f"""
@page {{ size: A4; margin: 2.2cm 2.3cm 2.4cm 2.3cm;
  @bottom-center {{ content: "{AVISO}"; font: 7pt 'DejaVu Sans'; color: #888; }}
  @bottom-right {{ content: "fl. " counter(page) "/" counter(pages); font: 8pt 'DejaVu Serif'; color: #555; }} }}
body {{ font-family: 'Liberation Serif', 'DejaVu Serif', serif; font-size: 11.2pt; line-height: 1.45; color: #111;
  text-align: justify; hyphens: manual; }}
p {{ margin: 0 0 0.55em 0; }}
strong {{ font-weight: bold; }}
p:has(> strong:only-child) {{ text-align: center; }}
table {{ border-collapse: collapse; width: 100%; margin: 0.6em 0 0.9em 0; font-size: 10pt; }}
th, td {{ border: 0.6pt solid #333; padding: 3pt 5pt; text-align: left; }}
pre {{ font-family: 'DejaVu Sans Mono', monospace; font-size: 8.4pt; border: 1.2pt solid #1b3a6b; color: #1b3a6b;
  padding: 7pt 9pt; white-space: pre-wrap; margin-top: 1.4em; transform: rotate(-0.6deg); }}
code {{ font-family: inherit; }}
hr {{ border: 0; border-top: 0.6pt dashed #666; margin: 1.2em 0; }}
"""

CSS_CRLV = f"""
@page {{ size: A4; margin: 1.6cm; @bottom-center {{ content: "{AVISO}"; font: 7pt 'DejaVu Sans'; color: #888; }} }}
body {{ font-family: 'DejaVu Sans', sans-serif; font-size: 9pt; color: #111; }}
.cab {{ border: 1.2pt solid #222; padding: 6pt 8pt; text-align: center; }}
.cab h1 {{ font-size: 11pt; margin: 2pt 0; letter-spacing: .5pt; }}
.cab p {{ margin: 1pt 0; font-size: 8pt; }}
.marca {{ position: fixed; top: 42%; left: 0; right: 0; text-align: center; font-size: 34pt; color: rgba(200,0,0,.12);
  transform: rotate(-24deg); font-weight: bold; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 8pt; }}
td {{ border: .8pt solid #444; padding: 4pt 6pt; vertical-align: top; }}
td span {{ display: block; font-size: 6.8pt; color: #555; text-transform: uppercase; letter-spacing: .3pt; }}
td b {{ font-size: 10pt; }}
"""

CSS_ATPV = f"""
@page {{ size: A4; margin: 1.6cm; @bottom-center {{ content: "{AVISO}"; font: 7pt 'DejaVu Sans'; color: #888; }} }}
body {{ font-family: 'DejaVu Sans', sans-serif; font-size: 9.4pt; color: #111; }}
.cab {{ border: 1.2pt solid #1b3a6b; padding: 6pt 8pt; text-align: center; color: #1b3a6b; }}
.cab h1 {{ font-size: 11pt; margin: 2pt 0; letter-spacing: .4pt; }}
.cab p {{ margin: 1pt 0; font-size: 8pt; color: #333; }}
.marca {{ position: fixed; top: 42%; left: 0; right: 0; text-align: center; font-size: 34pt; color: rgba(200,0,0,.12);
  transform: rotate(-24deg); font-weight: bold; }}
h2 {{ font-size: 9pt; background: #e8edf5; color: #1b3a6b; padding: 3pt 6pt; margin: 10pt 0 4pt; letter-spacing: .3pt; }}
p.c {{ margin: 2pt 6pt; }}
p.c b {{ font-weight: bold; }}
"""

COMPRADORES = [("Rita de Cássia Moreira", "Fortaleza/CE"), ("Jefferson Lucas Araújo", "Caucaia/CE"),
               ("Auto Center Litoral Ltda.", "Fortaleza/CE"), ("Patrícia Lemos Barroso", "Sobral/CE"),
               ("Frota Fácil Locações Ltda.", "Maracanaú/CE"), ("Diego Fernandes Uchoa", "Juazeiro do Norte/CE")]


def md_para_pdf(md_texto: str, destino: Path) -> None:
    html = markdown.markdown(md_texto, extensions=["tables", "fenced_code", "sane_lists"])
    HTML(string=f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{html}</body></html>").write_pdf(destino)


def crlv_html(caso: dict) -> str:
    v = SPEC["veiculos"][caso["veiculo"]]
    dono = caso["crlv_proprietario"]
    if dono["tipo"] == "PJ":
        e = SPEC["empresas"][dono["empresa"]]
        nome, doc, local = e["razao_social"], e["cnpj"], e["cidade"]
    else:
        p = SPEC["pessoas"][dono["pessoa"]]
        nome, doc, local = p["nome"].upper(), p["cpf"], p["cidade"]
    rng = random.Random(caso["id"])
    crv = f"{rng.randint(10**11, 10**12 - 1)}"
    cod_seg = f"{rng.randint(10**10, 10**11 - 1)}"
    campos = [
        ("Código RENAVAM", v["renavam"]), ("Placa", v["placa"]), ("Exercício", "2026"),
        ("Ano fabricação", v["ano_fabricacao"]), ("Ano modelo", v["ano_modelo"]), ("Número do CRV", crv),
        ("Código de segurança do CLA", cod_seg), ("Marca / Modelo / Versão", v["marca_modelo"]),
        ("Espécie / Tipo", v["especie_tipo"]), ("Chassi", v["chassi"]), ("Cor predominante", v["cor"]),
        ("Combustível", v["combustivel"]), ("Nome", nome), ("CPF / CNPJ", doc), ("Local", local.upper()),
        ("Data", "15/01/2026"),
    ]
    linhas, atual = [], []
    for i, (k, val) in enumerate(campos):
        largura = 3 if k in ("Marca / Modelo / Versão", "Nome", "Chassi") else 1
        atual.append(f"<td colspan='{largura}'><span>{k}</span><b>{val}</b></td>")
        if sum(3 if "colspan='3'" in c else 1 for c in atual) >= 3:
            linhas.append("<tr>" + "".join(atual) + "</tr>")
            atual = []
    if atual:
        linhas.append("<tr>" + "".join(atual) + "</tr>")
    return (f"<html><head><meta charset='utf-8'><style>{CSS_CRLV}</style></head><body>"
            "<div class='marca'>DOCUMENTO SIMULADO</div>"
            "<div class='cab'><h1>CERTIFICADO DE REGISTRO E LICENCIAMENTO DE VEÍCULO</h1>"
            "<p>Reprodução simulada para testes de software — sem valor legal</p></div>"
            f"<table>{''.join(linhas)}</table>"
            "<p style='margin-top:10pt;font-size:7.5pt;color:#444'>Observações: sem restrições. "
            "Documento gerado para o corpus sintético de avaliação.</p></body></html>")


def _br(data: str) -> str:
    a, m, d = data.split("-")
    return f"{d}/{m}/{a}"


def _moeda(v: float) -> str:
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _parte_atpv(x: dict) -> tuple[str, str, str]:
    if "empresa" in x:
        e = SPEC["empresas"][x["empresa"]]
        return e["razao_social"], e["cnpj"], e["cidade"]
    p = SPEC["pessoas"][x["pessoa"]]
    return p["nome"].upper(), p["cpf"], p["cidade"]


def atpv_html(caso: dict) -> str:
    """ATPV-e simulada (layout próprio, com os campos da autorização digital); assinaturas pendentes ou registradas."""
    v = SPEC["veiculos"][caso["veiculo"]]
    t = caso["transacao"]
    rng = random.Random("atpv" + caso["id"])
    blocos = []
    for titulo, campos in [
        ("IDENTIFICAÇÃO DO VEÍCULO", [("Placa", v["placa"]), ("RENAVAM", v["renavam"]), ("Chassi", v["chassi"]),
                                      ("Marca / Modelo", v["marca_modelo"]),
                                      ("Ano de fabricação / modelo", f"{v['ano_fabricacao']}/{v['ano_modelo']}"),
                                      ("Cor", v["cor"]), ("Código de segurança do CRV", f"{rng.randint(10**10, 10**11 - 1)}")]),
        ("IDENTIFICAÇÃO DO VENDEDOR (ANTIGO PROPRIETÁRIO)", list(zip(("Nome / Razão social", "CPF / CNPJ", "Município"),
                                                                    _parte_atpv(caso["vendedor"])))),
        ("IDENTIFICAÇÃO DO COMPRADOR (NOVO PROPRIETÁRIO)", list(zip(("Nome / Razão social", "CPF / CNPJ", "Município"),
                                                                   _parte_atpv(caso["comprador"])))),
        ("DADOS DA VENDA", [("Valor declarado da venda", _moeda(t["valor"])), ("Data da venda", _br(t["data_venda"]))]),
    ]:
        blocos.append(f"<h2>{titulo}</h2>" + "".join(f"<p class='c'>{k}: <b>{val}</b></p>" for k, val in campos))
    ass = []
    for lado in ("vendedor", "comprador"):
        x = caso[lado]
        nomes = [(SPEC["pessoas"][a["pessoa"]]["nome"].upper(), SPEC["pessoas"][a["pessoa"]]["cpf"])
                 for a in x.get("assinantes", [])] if "empresa" in x else [(SPEC["pessoas"][x["pessoa"]]["nome"].upper(),
                                                                            SPEC["pessoas"][x["pessoa"]]["cpf"])]
        if caso.get("assinaturas_na_atpv") and nomes:
            for n, cpf in nomes:
                ass.append(f"<p class='c'>Pelo {lado}: <b>{n}</b> (CPF {cpf}), assinado eletronicamente em "
                           f"{_br(t['data_venda'])} às {rng.randint(8, 17):02d}:{rng.randint(0, 59):02d}</p>")
        else:
            ass.append(f"<p class='c'>Pelo {lado}: assinatura pendente</p>")
    return (f"<html><head><meta charset='utf-8'><style>{CSS_ATPV}</style></head><body>"
            "<div class='marca'>DOCUMENTO SIMULADO</div>"
            "<div class='cab'><h1>AUTORIZAÇÃO PARA TRANSFERÊNCIA DE PROPRIEDADE DO VEÍCULO — DIGITAL (ATPV-e)</h1>"
            "<p>Reprodução simulada para testes de software — sem valor legal</p></div>"
            f"<p class='c'>Número da ATPV-e: <b>{caso['atpv_numero']}</b></p>"
            f"<p class='c'>Data de emissão: <b>{_br(t['data_venda'])}</b></p>"
            + "".join(blocos) + "<h2>ASSINATURAS ELETRÔNICAS</h2>" + "".join(ass) +
            "<p style='margin-top:12pt;font-size:7.5pt;color:#444'>As assinaturas eletrônicas são feitas no aplicativo, com "
            "conta gov.br. Documento gerado para o corpus sintético de avaliação.</p></body></html>")


def rasterizar(origem: Path, destino: Path, seed: str) -> None:
    """Simula digitalização: 150 dpi, leve rotação, desfoque e ruído, páginas como imagem."""
    rng = random.Random(seed)
    src = fitz.open(origem)
    out = fitz.open()
    for page in src:
        pix = page.get_pixmap(dpi=150, colorspace=fitz.csGRAY)
        img = Image.frombytes("L", (pix.width, pix.height), pix.samples)
        img = img.rotate(rng.uniform(-0.8, 0.8), resample=Image.BICUBIC, fillcolor=255, expand=False)
        img = img.filter(ImageFilter.GaussianBlur(0.45))
        px = img.load()
        for _ in range(img.width * img.height // 900):
            x, y = rng.randrange(img.width), rng.randrange(img.height)
            px[x, y] = rng.choice((0, 90, 200))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=72)
        nova = out.new_page(width=page.rect.width, height=page.rect.height)
        nova.insert_image(nova.rect, stream=buf.getvalue())
    out.save(destino, deflate=True)


def _com_cpfs(esp: dict | None) -> dict | None:
    if not esp:
        return None
    esp = dict(esp)
    pessoas = SPEC["pessoas"]
    esp["conjuntos_minimos_cpf"] = (None if esp["conjuntos_minimos"] is None else
                                    [[pessoas[p]["cpf"] for p in s] for s in esp["conjuntos_minimos"]])
    esp["conjuntos_minimos_nomes"] = (None if esp["conjuntos_minimos"] is None else
                                      [[pessoas[p]["nome"] for p in s] for s in esp["conjuntos_minimos"]])
    return esp


def main() -> None:
    import sys
    so_gabaritos = "--so-gabaritos" in sys.argv
    if "--apenas" in sys.argv:  # gera só os casos indicados, sem apagar os demais
        ids = set(sys.argv[sys.argv.index("--apenas") + 1:])
        todos = SPEC["casos"] + SPEC.get("casos_holdout", []) + SPEC.get("casos_atpv", []) + SPEC.get("casos_pf", [])
        PDF_DIR.mkdir(exist_ok=True)
        for i, caso in enumerate(todos):
            if caso["id"] not in ids:
                continue
            for did in caso["documentos"]:
                md = (AQUI / "docs" / f"{did}.md").read_text(encoding="utf-8")
                md_para_pdf(md, PDF_DIR / f"{did}.pdf")
            d = CASOS_DIR / caso["id"] / "docs"
            if d.parent.exists():
                shutil.rmtree(d.parent)
            d.mkdir(parents=True)
            for did in caso["documentos"]:
                shutil.copy(PDF_DIR / f"{did}.pdf", d / f"{did}.pdf")
            if "papel" not in caso:  # consulta por CPF: o dono vem da base veicular (sem CRLV)
                HTML(string=crlv_html(caso)).write_pdf(d / "CRLV.pdf")
            if "vendedor" in caso:  # lote ATPV-e
                HTML(string=atpv_html(caso)).write_pdf(d / "ATPV-e.pdf")
            _escrever_jsons(caso, i)
        print(f"{len(ids)} casos gerados")
        return
    if not so_gabaritos:
        PDF_DIR.mkdir(exist_ok=True)
        for did in SPEC["documentos"]:
            md = (AQUI / "docs" / f"{did}.md").read_text(encoding="utf-8")
            md_para_pdf(md, PDF_DIR / f"{did}.pdf")
        print(f"{len(SPEC['documentos'])} PDFs em {PDF_DIR}")
        if CASOS_DIR.exists():
            shutil.rmtree(CASOS_DIR)
    for i, caso in enumerate(SPEC["casos"] + SPEC.get("casos_holdout", []) + SPEC.get("casos_atpv", [])):
        d = CASOS_DIR / caso["id"] / "docs"
        if so_gabaritos:
            _escrever_jsons(caso, i)
            continue
        d.mkdir(parents=True)
        for did in caso["documentos"]:
            alvo = d / f"{did}.pdf"
            if caso.get("ocr"):
                rasterizar(PDF_DIR / f"{did}.pdf", alvo, f"{caso['id']}{did}")
            else:
                shutil.copy(PDF_DIR / f"{did}.pdf", alvo)
        HTML(string=crlv_html(caso)).write_pdf(d / "CRLV.pdf")
        if "vendedor" in caso:
            HTML(string=atpv_html(caso)).write_pdf(d / "ATPV-e.pdf")
        if caso.get("ocr"):
            rasterizar(d / "CRLV.pdf", d / "CRLV_scan.pdf", caso["id"] + "crlv")
            (d / "CRLV.pdf").unlink()
            (d / "CRLV_scan.pdf").rename(d / "CRLV.pdf")
        _escrever_jsons(caso, i)
    print(f"{len(SPEC['casos']) + len(SPEC.get('casos_holdout', [])) + len(SPEC.get('casos_atpv', []))} casos em {CASOS_DIR}")


def _parte_pedido(x: dict | None) -> dict | None:
    if not x:
        return None
    if "empresa" in x:
        e = SPEC["empresas"][x["empresa"]]
        return {"tipo": "PJ", "nome": e["razao_social"], "documento": e["cnpj"]}
    pe = SPEC["pessoas"][x["pessoa"]]
    return {"tipo": "PF", "nome": pe["nome"], "documento": pe["cpf"]}


def _escrever_jsons(caso: dict, i: int) -> None:
    if "papel" in caso:  # consulta por CPF antes da ATPV-e: só veículo + CPF + papel (o dono vem da base veicular)
        v = SPEC["veiculos"][caso["veiculo"]]
        pedido = {"caso": caso["id"], "veiculo": {"placa": v["placa"]}, "papel": caso["papel"],
                  "cpf": SPEC["pessoas"][caso["assinante"]]["cpf"], "data_venda": caso["transacao"]["data_venda"]}
        if caso["transacao"].get("valor") is not None:
            pedido["valor"] = caso["transacao"]["valor"]
        if caso.get("comprador"):
            pedido["comprador"] = _parte_pedido(caso["comprador"])
        (CASOS_DIR / caso["id"] / "pedido.json").write_text(json.dumps(pedido, ensure_ascii=False, indent=2), encoding="utf-8")
        gab = {"caso": caso["id"], "titulo": caso["titulo"], "categoria": caso["categoria"], "objetivo": caso["objetivo"],
               "validacao_cega": False, "lote": "pf", "esperado": _com_cpfs(caso["esperado"]),
               "esperado_ce": _com_cpfs(caso.get("esperado_ce")),
               "esperado_lados": {k: _com_cpfs(v) for k, v in caso["esperado_lados"].items()},
               "esperado_lados_ce": ({k: _com_cpfs(v) for k, v in caso["esperado_lados_ce"].items()}
                                     if caso.get("esperado_lados_ce") else None)}
        (CASOS_DIR / caso["id"] / "gabarito.json").write_text(json.dumps(gab, ensure_ascii=False, indent=2), encoding="utf-8")
        return
    if "vendedor" in caso:  # lote ATPV-e: o pedido traz só quem vai assinar; o resto sai da ATPV-e
        pedido: dict = {"caso": caso["id"], "forma_assinatura": "ATPV-e"}
        if not caso.get("assinaturas_na_atpv"):
            for lado in ("vendedor", "comprador"):
                x = caso[lado]
                pedido[lado] = {"assinantes": [{"nome": a["nome"], "cpf": a["cpf"]} for a in x.get("assinantes", [])]}
        (CASOS_DIR / caso["id"] / "pedido.json").write_text(json.dumps(pedido, ensure_ascii=False, indent=2), encoding="utf-8")
        gab = {"caso": caso["id"], "titulo": caso["titulo"], "categoria": caso["categoria"], "objetivo": caso["objetivo"],
               "validacao_cega": False, "lote": "atpv", "esperado": _com_cpfs(caso["esperado"]), "esperado_ce": None,
               "esperado_lados": {k: _com_cpfs(v) for k, v in caso["esperado_lados"].items()}}
        (CASOS_DIR / caso["id"] / "gabarito.json").write_text(json.dumps(gab, ensure_ascii=False, indent=2), encoding="utf-8")
        return
    if True:
        v = SPEC["veiculos"][caso["veiculo"]]
        emp = SPEC["empresas"][caso["empresa"]]
        comp_nome, comp_cid = COMPRADORES[i % len(COMPRADORES)]
        pedido = {
            "caso": caso["id"],
            "vendedor": {"razao_social": emp["razao_social"], "cnpj": emp["cnpj"]},
            "veiculo": {"placa": v["placa"], "renavam": v["renavam"], "chassi": v["chassi"], "descricao": v["marca_modelo"]},
            "data_venda": caso["transacao"]["data_venda"],
            "valor": caso["transacao"]["valor"],
            "assinantes": [{"nome": a["nome"], "cpf": a["cpf"]} for a in caso["transacao"]["assinantes"]],
            "comprador": {"nome": comp_nome, "cidade": comp_cid},
            "forma_assinatura": "ATPV-e",
        }
        (CASOS_DIR / caso["id"] / "pedido.json").write_text(json.dumps(pedido, ensure_ascii=False, indent=2), encoding="utf-8")
        gab = {"caso": caso["id"], "titulo": caso["titulo"], "categoria": caso["categoria"], "objetivo": caso["objetivo"],
               "validacao_cega": caso["id"].startswith("H"),
               "esperado": _com_cpfs(caso["esperado"]), "esperado_ce": _com_cpfs(caso.get("esperado_ce"))}
        (CASOS_DIR / caso["id"] / "gabarito.json").write_text(json.dumps(gab, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
