"""Outorga — agente de verificação de poderes para assinatura do ATPV por pessoa jurídica."""

import argparse
import json
import sys
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(prog="outorga", description="Verificação de poderes para ATPV (pessoa jurídica)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("serve", help="sobe a API e a interface web")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--porta", type=int, default=8765)
    a = sub.add_parser("analisar", help="analisa uma pasta com a ATPV-e e os documentos das empresas")
    a.add_argument("pasta")
    a.add_argument("--pedido", help="JSON com quem vai assinar por cada lado (padrão: <pasta>/pedido.json, se existir)")
    a.add_argument("--politica", default="ce")
    a.add_argument("--amostras", type=int, default=1)
    a.add_argument("--pdf", help="salva o parecer em PDF neste caminho")
    c = sub.add_parser("consultar", help="antes da ATPV-e: este CPF pode vender (ou comprar) este veículo?")
    c.add_argument("--placa")
    c.add_argument("--renavam")
    c.add_argument("--cpf", required=True, help="CPF de quem vai assinar")
    c.add_argument("--nome", help="nome de quem vai assinar (opcional)")
    c.add_argument("--papel", required=True, choices=["vender", "comprar"])
    c.add_argument("--comprador", help="CPF ou CNPJ do comprador (para --papel comprar)")
    c.add_argument("--valor", type=float, help="valor previsto da venda (para contratos com alçada)")
    c.add_argument("--politica", default="ce")
    c.add_argument("--pdf", help="salva o parecer em PDF neste caminho")
    c.add_argument("documentos", nargs="*", help="contrato social/estatuto, procuração, substabelecimento, CRLV...")
    g = sub.add_parser("agente", help="modo agente: processa sozinho os pedidos que chegam numa pasta")
    g.add_argument("--entrada", help="pasta vigiada (padrão: dados/agente/entrada)")
    g.add_argument("--saida", help="onde gravar pareceres (padrão: dados/agente/saida)")
    g.add_argument("--politica", help="ce ou generica (padrão: a política salva na interface web)")
    g.add_argument("--intervalo", type=float, default=5, help="segundos entre varreduras")
    g.add_argument("--estabilidade", type=float, default=10,
                   help="segundos sem mudança para considerar a pasta completa (ou crie o arquivo PRONTO)")
    g.add_argument("--uma-vez", action="store_true", help="processa o que houver na entrada e sai")
    g.add_argument("--amostras", type=int, default=1)
    v = sub.add_parser("avaliar", help="roda a avaliação contra o gabarito do corpus")
    v.add_argument("modo", choices=["oraculo", "llm"])
    v.add_argument("--casos", nargs="*")
    v.add_argument("--politica", default="ce")
    v.add_argument("--amostras", type=int, default=1)
    v.add_argument("--saida")
    args = ap.parse_args()

    if args.cmd == "serve":
        import uvicorn

        uvicorn.run("outorga.api:app", host=args.host, port=args.porta, log_level="info")
    elif args.cmd == "analisar":
        from .agente import resumo_texto
        from .engine import Politica
        from .extract import ler_pasta
        from .llm import provedor_padrao
        from .parecer import pdf_parecer
        from .pipeline import analisar_leituras

        pasta = Path(args.pasta)
        docs = pasta / "docs" if (pasta / "docs").is_dir() else pasta
        arq = Path(args.pedido) if args.pedido else pasta / "pedido.json"
        pedido = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}

        def progresso(tipo, d):
            if tipo in ("classificado", "tarefa_fim"):
                print(f"  · {d.get('nome') or d.get('doc')}: {d.get('titulo') or d.get('tarefa')} {d.get('resumo', '')}",
                      file=sys.stderr)

        leituras = ler_pasta(docs, provedor_padrao(), args.amostras, progresso)
        res = analisar_leituras(leituras, pedido, Politica.por_nome(args.politica))
        print("\n" + resumo_texto(res, pasta.name))
        if args.pdf:
            Path(args.pdf).write_bytes(pdf_parecer(res))
            print(f"parecer: {args.pdf}")
    elif args.cmd == "consultar":
        from .agente import resumo_texto
        from .engine import Politica
        from .extract import ler_arquivos
        from .llm import provedor_padrao
        from .parecer import pdf_parecer
        from .pipeline import analisar_leituras

        pedido = {"veiculo": {"placa": args.placa, "renavam": args.renavam}, "cpf": args.cpf, "nome": args.nome,
                  "papel": args.papel, "valor": args.valor}
        if args.comprador:
            pedido["comprador"] = {"documento": args.comprador}
        arquivos = [Path(a) for a in args.documentos]
        leituras = ler_arquivos(arquivos, provedor_padrao(), 1) if arquivos else []
        res = analisar_leituras(leituras, pedido, Politica.por_nome(args.politica))
        print(resumo_texto(res, f"consulta {args.cpf}"))
        if args.pdf:
            Path(args.pdf).write_bytes(pdf_parecer(res))
            print(f"parecer: {args.pdf}")
    elif args.cmd == "agente":
        from . import store
        from .agente import Agente
        from .engine import Politica

        ag = Agente(Path(args.entrada) if args.entrada else store.DADOS / "agente" / "entrada",
                    Path(args.saida) if args.saida else store.DADOS / "agente" / "saida",
                    Politica.por_nome(args.politica) if args.politica else None,
                    args.intervalo, args.estabilidade, args.amostras)
        sys.exit(ag.rodar(uma_vez=args.uma_vez))
    elif args.cmd == "avaliar":
        from .avaliacao import RESULTADOS, rodar
        from .engine import Politica
        from datetime import datetime

        prov = None
        if args.modo == "llm":
            from .llm import provedor_padrao
            prov = provedor_padrao()
        saida = Path(args.saida) if args.saida else RESULTADOS / f"{args.modo}-{datetime.now():%Y%m%d-%H%M%S}"
        rodar(args.modo, args.casos, Politica.por_nome(args.politica), prov, args.amostras, saida)
