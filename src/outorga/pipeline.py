"""Pipeline ponta a ponta: documentos → leitura → consolidação → motor → índice/faixa → resultado serializado."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path
from typing import Any, Callable

from .consolidate import Consolidador, LeituraDocumento
import re

from .domain import Assinante, Faixa, Parte, Pedido, PedidoATPV, Severidade, VeiculoId, para_json
from .ids import similaridade_nomes, so_digitos
from .engine import Motor, Politica, Resultado
from .lexicon import parse_data
from .parecer import comprovacao_poderes
from .scoring import Avaliacao, avaliar

VERSAO = "0.1.0"

Progresso = Callable[[str, dict], None]


def _parte(x: Any, tipo_padrao: str | None, assinantes_legado: list | None = None) -> Parte:
    if not isinstance(x, dict):
        x = {"nome": x} if x else {}
    doc = x.get("documento") or x.get("cnpj") or x.get("cpf")
    d = so_digitos(doc)
    tipo = x.get("tipo") or ("PJ" if len(d) == 14 else "PF" if len(d) == 11 else tipo_padrao or "PF")
    ass = x.get("assinantes") if x.get("assinantes") is not None else (assinantes_legado or [])
    return Parte(tipo, x.get("nome") or x.get("razao_social"), doc, [Assinante(a["nome"], a.get("cpf")) for a in ass if a.get("nome")])


PAPEIS = {"vender": "vendedor", "vendedor": "vendedor", "venda": "vendedor",
          "comprar": "comprador", "comprador": "comprador", "compra": "comprador"}


def pedido_cpf_de_json(d: dict) -> PedidoATPV:
    """Consulta ANTES da ATPV-e: veículo + CPF de quem vai assinar + se vai vender ou comprar.
    O proprietário vem da base veicular (ou do CRLV anexado); o comprador, do pedido. Só o lado do CPF é verificado."""
    from . import base_veicular
    from .ids import cpf_valido

    lado = PAPEIS.get(str(d.get("papel", "")).lower())
    if not lado:
        raise ValueError("informe o papel de quem vai assinar: 'vender' ou 'comprar'")
    cpf = d.get("cpf")
    if not cpf_valido(cpf):
        raise ValueError(f"CPF inválido: {cpf}")
    v = d.get("veiculo") or {}
    veic = VeiculoId(v.get("descricao"), v.get("placa"), v.get("renavam"), v.get("chassi"))
    if not (veic.placa or veic.renavam or veic.chassi):
        raise ValueError("informe a placa ou o RENAVAM do veículo")
    vendedor = _parte(d.get("vendedor"), "PJ") if d.get("vendedor") else Parte("PJ")
    fonte = "informado" if d.get("vendedor") else None
    achado = None if d.get("vendedor") else base_veicular.consultar(veic.placa, veic.renavam)
    if achado:
        pr = achado["proprietario"]
        vendedor = _parte(pr, "PJ")
        veic.placa, veic.renavam = veic.placa or achado.get("placa"), veic.renavam or achado.get("renavam")
        veic.chassi, veic.descricao = veic.chassi or achado.get("chassi"), veic.descricao or achado.get("marca_modelo")
        fonte = "base veicular"
    comprador = _parte(d.get("comprador"), None) if d.get("comprador") else Parte("PF")
    assinante = Assinante(d.get("nome") or f"CPF {cpf}", cpf)
    (vendedor if lado == "vendedor" else comprador).assinantes = [assinante]
    data = d.get("data_venda") or d.get("data")
    valor = d.get("valor")
    return PedidoATPV(veic, (parse_data(data) if isinstance(data, str) else data) or date.today(),
                      float(valor) if valor not in (None, "") else None, vendedor, comprador,
                      d.get("forma_assinatura", "ATPV-e"), "consulta por CPF", lado, fonte)


def pedido_atpv_de_json(d: dict) -> PedidoATPV:
    """Aceita o formato novo (vendedor/comprador com tipo, documento e assinantes), o antigo (assinantes do vendedor)
    e a consulta por CPF antes da ATPV-e ({veiculo, cpf, papel: vender|comprar})."""
    if d.get("cpf") and d.get("papel"):
        return pedido_cpf_de_json(d)
    v = d.get("veiculo") or {}
    valor = d.get("valor")
    data = d.get("data_venda")
    return PedidoATPV(
        veiculo=VeiculoId(v.get("descricao"), v.get("placa"), v.get("renavam"), v.get("chassi")),
        data_venda=(parse_data(data) if isinstance(data, str) else data),
        valor=float(valor) if valor not in (None, "") else None,
        vendedor=_parte(d.get("vendedor"), "PJ", d.get("assinantes")),
        comprador=_parte(d.get("comprador"), None),
        forma_assinatura=d.get("forma_assinatura", "ATPV-e"),
        origem=d.get("origem", "informado"),
        alvo=d.get("alvo"),                    # pedido já resolvido de uma consulta por CPF (simulação)
        titular_fonte=d.get("titular_fonte"),
    )


def pedido_de_json(d: dict) -> Pedido:
    v = d.get("veiculo", {})
    valor = d.get("valor")
    return Pedido(
        veiculo=VeiculoId(v.get("descricao"), v.get("placa"), v.get("renavam"), v.get("chassi")),
        data_venda=parse_data(d["data_venda"]) if isinstance(d["data_venda"], str) else d["data_venda"],
        valor=float(valor) if valor not in (None, "") else None,
        assinantes=[Assinante(a["nome"], a.get("cpf")) for a in d.get("assinantes", [])],
        forma_assinatura=d.get("forma_assinatura", "ATPV-e"),
        comprador=(d.get("comprador") or {}).get("nome") if isinstance(d.get("comprador"), dict) else d.get("comprador"),
        vendedor_cnpj=(d.get("vendedor") or {}).get("cnpj") if isinstance(d.get("vendedor"), dict) else None,
    )


def _fonte(f) -> dict | None:
    return para_json(f) if f else None


def serializar(res: Resultado, av: Avaliacao, motor: Motor, pedido: Pedido, leituras: list[LeituraDocumento],
               meta: dict | None = None) -> dict[str, Any]:
    kb = motor.kb
    nome = motor.nome

    def alt(a):
        return {"id": a.id, "pessoas": [{"chave": p, "nome": nome(p)} for p in sorted(a.pessoas, key=nome)],
                "via": a.via, "descricao": a.descricao, "cadeia": a.cadeia, "severidade": a.severidade.value,
                "confianca": round(a.confianca, 3),
                "achados": [para_json(x) for x in a.achados],
                "precondicoes": [para_json(p) for p in a.precondicoes]}

    regras_txt = []
    for item in res.formula.avaliacao:
        r = next((r for ato in kb.atos for r in ato.regras if r.id == item["regra"]), None)
        regras_txt.append({**{k: v for k, v in item.items() if k != "fonte"}, "fonte": _fonte(item["fonte"]),
                           "modo": r.modo if r else None, "pessoas": [nome(p) for p in (r.pessoas if r else [])],
                           "cargo": r.cargo if r else None, "valor_acima_de": r.valor_acima_de if r else None,
                           "confianca": r.confianca if r else None,
                           "verificacoes": [para_json(v) for v in (r.verificacoes if r else [])],
                           "decisiva": bool(r and r in res.formula.regras)})
    docs = []
    for l in leituras:
        d = l.doc
        docs.append({"id": d.id, "nome": d.nome, "tipo": l.classificacao.tipo, "titulo": l.classificacao.titulo,
                     "data": l.classificacao.data_documento, "paginas": d.paginas, "metodo": d.metodo,
                     "ocr_confianca": d.ocr_confianca, "sha256": d.sha256, "leitura": l.meta})
    return {
        "versao": VERSAO,
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "pedido": para_json(pedido),
        "empresa": para_json(kb.empresa),
        "veredito": res.veredito.value,
        "faixa": av.faixa.value,
        "indice": av.indice,
        "confianca": av.confianca,
        "componentes": av.componentes,
        "motivos_faixa": av.motivos,
        "resumo": res.resumo,
        "assinantes": res.assinantes,
        "quem_pode": [alt(a) for a in res.alternativas],
        "caminhos_invalidos": [alt(a) for a in res.bloqueadas],
        "caminho_escolhido": alt(res.escolhida) if res.escolhida else None,
        "faltantes": [{**f, "faltam_nomes": [nome(p) for p in f["faltam"]], "pessoas_nomes": [nome(p) for p in f["pessoas"]]}
                      for f in res.faltantes],
        "achados": [para_json(a) for a in res.achados],
        "regras": regras_txt,
        "precondicoes": [para_json(p) for p in res.formula.precondicoes],
        "regime": {
            "data": res.regime.data.isoformat(),
            "atos": [{"doc": a.doc_id, "titulo": a.titulo, "efeito": a.data_efeito.isoformat() if a.data_efeito else None}
                     for a in res.regime.atos],
            "administradores": [{"chave": a.pessoa, "nome": nome(a.pessoa), "cargo": a.cargo, "doc": a.fonte.doc_id}
                                for a in res.regime.administradores],
            "encerrados": [{"nome": nome(a.pessoa), "motivo": m} for a, m in res.regime.encerrados],
            "socios": [{"chave": k, "nome": nome(k), "percentual": v} for k, v in res.regime.socios.items()],
        },
        "grafo": para_json(res.grafo),
        "linha_do_tempo": para_json(res.linha_do_tempo),
        "pessoas": {k: {"nome": p.nome, "cpf": p.cpf} for k, p in kb.pessoas.items()},
        "comprovacao_poderes": comprovacao_poderes(res, motor, pedido),
        "documentos": docs,
        "avisos": kb.avisos,
        "meta": meta or {},
    }


_RE_CNPJ = re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")


def _cnpjs_da_leitura(l: LeituraDocumento) -> tuple[set[str], str | None]:
    """CNPJs ligados a um documento: (todos os citados no texto, o 'dono' segundo os campos extraídos)."""
    dono = None
    if l.partes and l.partes.empresa.cnpj:
        dono = so_digitos(l.partes.empresa.cnpj)
    elif l.procuracao and l.procuracao.outorgante.tipo == "PJ":
        dono = so_digitos(l.procuracao.outorgante.documento)
    elif l.revogacao and l.revogacao.revogante.tipo == "PJ":
        dono = so_digitos(l.revogacao.revogante.documento)
    elif l.crlv:
        dono = so_digitos(l.crlv.proprietario_documento)
    citados = {so_digitos(m.group(0)) for m in _RE_CNPJ.finditer(l.doc.texto)}
    return citados, (dono or None)


def _nome_da_leitura(l: LeituraDocumento) -> str | None:
    if l.partes:
        return l.partes.empresa.razao_social
    if l.procuracao:
        return l.procuracao.outorgante.nome
    if l.revogacao:
        return l.revogacao.revogante.nome
    return None


def leituras_da_parte(leituras: list[LeituraDocumento], pedido: PedidoATPV, lado: str) -> list[LeituraDocumento]:
    """Separa os documentos de cada empresa. Com só um lado PJ, todos os documentos (menos a ATPV-e) vão para ele."""
    parte = pedido.vendedor if lado == "vendedor" else pedido.comprador
    outra = pedido.comprador if lado == "vendedor" else pedido.vendedor
    docs = [l for l in leituras if not l.atpv]
    if outra.tipo != "PJ":
        return docs if lado == "vendedor" else [l for l in docs if not l.crlv]
    alvo, outro = so_digitos(parte.documento), so_digitos(outra.documento)
    out = []
    for l in docs:
        if l.crlv:
            if lado == "vendedor":
                out.append(l)
            continue
        citados, dono = _cnpjs_da_leitura(l)
        if dono:
            if dono == alvo:
                out.append(l)
            continue
        if alvo and alvo in citados and outro not in citados:
            out.append(l)
            continue
        nome = _nome_da_leitura(l) or ""
        if nome and parte.nome and similaridade_nomes(nome, parte.nome) >= 85:
            out.append(l)
        elif not nome and parte.nome and similaridade_nomes(l.doc.texto[:400], parte.nome) >= 85:
            out.append(l)
    return out


def completar_com_atpv(pedido: PedidoATPV, leituras: list[LeituraDocumento]) -> tuple[PedidoATPV, list[str]]:
    """Preenche com a própria ATPV-e o que o pedido não trouxe (veículo, partes, valor, data) e aponta divergências."""
    avisos = []
    a = next((l.atpv for l in leituras if l.atpv), None)
    if a is None:
        return pedido, avisos
    v = pedido.veiculo
    v.placa, v.renavam, v.chassi = v.placa or a.placa, v.renavam or a.renavam, v.chassi or a.chassi
    v.descricao = v.descricao or a.marca_modelo
    if a.placa and pedido.veiculo.placa and so_digitos(a.placa) + a.placa[:3] != so_digitos(pedido.veiculo.placa) + pedido.veiculo.placa[:3]:
        avisos.append(f"Placa do pedido ({pedido.veiculo.placa}) diverge da ATPV-e ({a.placa}).")
    if pedido.data_venda is None and a.data:
        pedido.data_venda = parse_data(a.data)
    if pedido.valor is None and a.valor is not None:
        pedido.valor = a.valor
    for lado, pa in (("vendedor", a.vendedor), ("comprador", a.comprador)):
        parte = pedido.vendedor if lado == "vendedor" else pedido.comprador
        if not parte.documento:
            parte.documento, parte.tipo = pa.documento, pa.tipo
        elif pa.documento and so_digitos(pa.documento) != so_digitos(parte.documento):
            avisos.append(f"Documento do {lado} no pedido diverge da ATPV-e ({pa.documento}).")
        parte.nome = parte.nome or pa.nome
        if not parte.assinantes:
            parte.assinantes = [Assinante(s.nome, s.cpf) for s in a.assinaturas if s.lado == lado]
    pedido.origem = "ATPV-e"
    return pedido, avisos


def completar_com_crlv(pedido: PedidoATPV, leituras: list[LeituraDocumento]) -> PedidoATPV:
    """Sem a base veicular, o proprietário (vendedor) sai do CRLV anexado."""
    c = next((l.crlv for l in leituras if l.crlv), None)
    if c is None or pedido.vendedor.documento:
        return pedido
    d = so_digitos(c.proprietario_documento)
    pedido.vendedor.documento = c.proprietario_documento
    pedido.vendedor.nome = pedido.vendedor.nome or c.proprietario_nome
    pedido.vendedor.tipo = "PJ" if len(d) == 14 else "PF" if len(d) == 11 else pedido.vendedor.tipo
    v = pedido.veiculo
    v.placa, v.renavam, v.chassi = v.placa or c.placa, v.renavam or c.renavam, v.chassi or c.chassi
    v.descricao = v.descricao or c.marca_modelo
    pedido.titular_fonte = pedido.titular_fonte or "CRLV"
    return pedido


def _precisa_verificar_pf(parte: Parte) -> bool:
    """Pessoa física só é verificada quando alguém assina POR ela (CPF ou nome diferente do titular)."""
    cpf_t = so_digitos(parte.documento)
    for a in parte.assinantes:
        cpf_a = so_digitos(a.cpf)
        if cpf_a and cpf_t:
            if cpf_a != cpf_t:
                return True
        elif not (parte.nome and similaridade_nomes(a.nome, parte.nome) >= 90):
            return True
    return False


def leituras_da_pf(leituras: list[LeituraDocumento], pedido: PedidoATPV, lado: str) -> list[LeituraDocumento]:
    """Documentos de um lado pessoa física: procurações/substabelecimentos/revogações (e o CRLV, se for o vendedor)
    que não sejam claramente da outra parte."""
    parte = pedido.vendedor if lado == "vendedor" else pedido.comprador
    outra = pedido.comprador if lado == "vendedor" else pedido.vendedor
    alvo, outro = so_digitos(parte.documento), so_digitos(outra.documento)
    out = []
    for l in leituras:
        if l.atpv or l.partes or l.ata:
            continue
        if l.crlv:
            if lado == "vendedor":
                out.append(l)
            continue
        if l.procuracao:
            o = l.procuracao.outorgante
            dono = so_digitos(o.documento)
            if dono and outro and dono == outro and dono != alvo:
                continue
            if not dono and outra.nome and o.nome and similaridade_nomes(o.nome, outra.nome) >= 90 and not (
                    parte.nome and similaridade_nomes(o.nome, parte.nome) >= 90):
                continue
        out.append(l)
    return out


_PENDENCIAS = {  # achado → o que pedir a quem está no balcão (a tela e o agente usam isto para "perguntar")
    "PROCURACAO_NECESSARIA": "procuracao",
    "SEM_ATO_CONSTITUTIVO": "ato_constitutivo",
    "LACUNA_DE_ALTERACOES": "alteracoes",
    "VALOR_NAO_INFORMADO": "valor",
    "DELIBERACAO_SOCIOS": "ata_aprovacao",
    "CRLV_NAO_APRESENTADO": "crlv",
}


def _pendencias(r: dict) -> list[dict]:
    achados = r["achados"] + ((r.get("caminho_escolhido") or {}).get("achados") or [])
    out, vistos = [], set()
    for a in achados:
        tipo = _PENDENCIAS.get(a["codigo"])
        if tipo and tipo not in vistos and a["severidade"] in ("alerta", "bloqueio"):
            vistos.add(tipo)
            out.append({"tipo": tipo, "mensagem": a["detalhe"]})
    return out


def _combinar(lados: dict[str, dict]) -> dict:
    faixas = [r["faixa"] for r in lados.values()]
    vereditos = [r["veredito"] for r in lados.values()]
    faixa = "VERMELHO" if "VERMELHO" in faixas else "AMARELO" if "AMARELO" in faixas else "VERDE"
    veredito = "NAO_PODE" if "NAO_PODE" in vereditos else "INDETERMINADO" if "INDETERMINADO" in vereditos else "PODE"
    nomes = {"vendedor": "Vendedor", "comprador": "Comprador"}
    return {"veredito": veredito, "faixa": faixa, "indice": min(r["indice"] for r in lados.values()),
            "resumo": " · ".join(f"{nomes[k]}: {r['resumo']}" for k, r in lados.items()),
            "motivos_faixa": [f"{nomes[k]} — {m}" for k, r in lados.items() for m in r["motivos_faixa"]],
            "lados": list(lados)}


def analisar_leituras(leituras: list[LeituraDocumento], pedido: Pedido | PedidoATPV | dict,
                      politica: Politica | None = None, meta: dict | None = None) -> dict[str, Any]:
    """Verifica os poderes de quem assina pela(s) pessoa(s) jurídica(s) da ATPV-e: vendedor e/ou comprador."""
    pol = politica or Politica()
    if isinstance(pedido, dict):
        pedido = pedido_atpv_de_json(pedido)
    if isinstance(pedido, Pedido):  # formato antigo: só o vendedor
        pedido = PedidoATPV(pedido.veiculo, pedido.data_venda, pedido.valor,
                            Parte("PJ", None, pedido.vendedor_cnpj, list(pedido.assinantes)),
                            Parte("PF", pedido.comprador, None, []), pedido.forma_assinatura)
    pedido, avisos_atpv = completar_com_atpv(pedido, leituras)
    pedido = completar_com_crlv(pedido, leituras)
    if pedido.data_venda is None:
        raise ValueError("data da venda não informada (nem encontrada na ATPV-e)")
    if pedido.alvo == "vendedor" and not pedido.vendedor.documento:
        raise ValueError("não encontrei o proprietário do veículo: informe a placa/RENAVAM cadastrados ou anexe o CRLV")
    meta = {**(meta or {}), "politica": pol.nome}
    lados: dict[str, dict] = {}
    for lado, parte in (("vendedor", pedido.vendedor), ("comprador", pedido.comprador)):
        if pedido.alvo and lado != pedido.alvo:
            continue  # consulta por CPF: só o lado de quem vai assinar
        if parte.tipo == "PF":
            if not (pedido.alvo == lado or _precisa_verificar_pf(parte)):
                continue  # o próprio titular assina: nada a comprovar
            ls = leituras_da_pf(leituras, pedido, lado)
            origem = ("Base veicular (simulada)" if lado == "vendedor" and pedido.titular_fonte == "base veicular" else
                      "CRLV" if lado == "vendedor" and pedido.titular_fonte == "CRLV" else "Pedido / ATPV-e")
            kb = Consolidador(ls).consolidar_pf(parte.nome, parte.documento, origem)
        else:
            ls = leituras_da_parte(leituras, pedido, lado)
            kb = Consolidador(ls).consolidar()
        if lado == "vendedor" and pedido.titular_fonte == "base veicular":
            kb.titular_fonte = "base veicular"
        motor = Motor(kb, pol)
        p_lado = pedido.lado(lado)
        res = motor.analisar(p_lado)
        av = avaliar(res, pol)
        r = serializar(res, av, motor, p_lado, ls, meta)
        r["lado"] = lado
        r["pendencias"] = _pendencias(r)
        if parte.tipo == "PF":
            r["empresa"].update({"cnpj": None, "cpf": parte.documento})
        elif not any(l.partes for l in ls):  # sem ato constitutivo: identifica a empresa pelo pedido/ATPV-e
            if r["empresa"].get("razao_social") in (None, "", "(empresa não identificada)"):
                r["empresa"]["razao_social"] = parte.nome or "(empresa não identificada)"
            r["empresa"]["cnpj"] = r["empresa"].get("cnpj") or parte.documento
            if not ls:
                papel = "vendedora" if lado == "vendedor" else "compradora"
                r["resumo"] = (f"Nenhum documento da empresa {papel} ({parte.nome or parte.documento or 'não identificada'}) "
                               f"foi apresentado: não dá para verificar quem pode assinar por ela. Anexe o ato constitutivo "
                               f"(contrato social/estatuto e alterações) e, se houver, a procuração.")
        lados[lado] = r
    if not lados:
        raise ValueError("nenhuma das partes da ATPV-e é pessoa jurídica: a verificação de poderes do § 7º não se aplica")
    primario = lados.get("vendedor") or lados["comprador"]
    out = dict(primario)
    out["lados"] = lados
    out["geral"] = _combinar(lados)
    if len(lados) > 1:
        for k in ("veredito", "faixa", "indice", "resumo", "motivos_faixa"):
            out[k] = out["geral"][k]
    out["pedido_atpv"] = para_json(pedido)
    out["pendencias"] = [{**pd, "lado": k} for k, r in lados.items() for pd in r["pendencias"]]
    out["avisos"] = list(out.get("avisos", [])) + avisos_atpv
    out["hash_entrada"] = hashlib.sha256(json.dumps(
        {"docs": [l.doc.sha256 for l in leituras], "pedido": para_json(pedido)}, sort_keys=True, default=str).encode()).hexdigest()
    return out
