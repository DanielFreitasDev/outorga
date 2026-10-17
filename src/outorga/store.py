"""Persistência (SQLite) + trilha de auditoria encadeada por hash.

Cada evento relevante (análise concluída, revisão humana, mudança de política) entra na cadeia:
    hash_n = SHA-256(hash_{n-1} | tipo | analise | sha256(payload) | instante)
Alterar qualquer registro antigo quebra todos os hashes seguintes — `verificar_cadeia()` detecta.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from dataclasses import fields

from .consolidate import LeituraDocumento
from .domain import Severidade
from .engine import Politica
from .ingest import Documento, _calc_offsets
from . import schemas as sc

RAIZ = Path(__file__).resolve().parents[2]
DADOS = RAIZ / "dados"
_lock = threading.Lock()

SQL = """
CREATE TABLE IF NOT EXISTS analises (
  id TEXT PRIMARY KEY, criado_em TEXT, atualizado_em TEXT, status TEXT, origem TEXT, caso_demo TEXT,
  empresa TEXT, cnpj TEXT, placa TEXT, veredito TEXT, faixa TEXT, indice REAL, provedor TEXT, politica TEXT,
  pedido_json TEXT, resultado_json TEXT, erro TEXT, duracao_s REAL
);
CREATE TABLE IF NOT EXISTS revisoes (
  id INTEGER PRIMARY KEY AUTOINCREMENT, analise_id TEXT, criado_em TEXT, revisor TEXT, decisao TEXT, justificativa TEXT
);
CREATE TABLE IF NOT EXISTS auditoria (
  seq INTEGER PRIMARY KEY AUTOINCREMENT, criado_em TEXT, tipo TEXT, analise_id TEXT, payload_hash TEXT,
  hash_anterior TEXT, hash TEXT, resumo TEXT
);
CREATE TABLE IF NOT EXISTS config (chave TEXT PRIMARY KEY, valor TEXT);
"""


def conectar() -> sqlite3.Connection:
    DADOS.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DADOS / "outorga.db", check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.executescript(SQL)
    return c


_con = None


def con() -> sqlite3.Connection:
    global _con
    if _con is None:
        _con = conectar()
    return _con


def agora() -> str:
    return datetime.now().isoformat(timespec="seconds")


# ------------------------------------------------------------------------------------ auditoria
def auditar(tipo: str, analise_id: str | None, payload: Any, resumo: str = "") -> str:
    with _lock:
        c = con()
        ult = c.execute("SELECT hash FROM auditoria ORDER BY seq DESC LIMIT 1").fetchone()
        anterior = ult["hash"] if ult else "0" * 64
        ph = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()
        t = agora()
        h = hashlib.sha256(f"{anterior}|{tipo}|{analise_id or ''}|{ph}|{t}".encode()).hexdigest()
        c.execute("INSERT INTO auditoria (criado_em, tipo, analise_id, payload_hash, hash_anterior, hash, resumo) "
                  "VALUES (?,?,?,?,?,?,?)", (t, tipo, analise_id, ph, anterior, h, resumo))
        c.commit()
        return h


def verificar_cadeia() -> dict:
    anterior, n, quebra = "0" * 64, 0, None
    for r in con().execute("SELECT * FROM auditoria ORDER BY seq"):
        n += 1
        esperado = hashlib.sha256(f"{anterior}|{r['tipo']}|{r['analise_id'] or ''}|{r['payload_hash']}|{r['criado_em']}".encode()).hexdigest()
        if r["hash_anterior"] != anterior or r["hash"] != esperado:
            quebra = r["seq"]
            break
        anterior = r["hash"]
    return {"registros": n, "integra": quebra is None, "quebra_em": quebra, "ultimo_hash": anterior}


def listar_auditoria(limite: int = 200) -> list[dict]:
    return [dict(r) for r in con().execute("SELECT * FROM auditoria ORDER BY seq DESC LIMIT ?", (limite,))]


# ------------------------------------------------------------------------------------- análises
def criar_analise(aid: str, origem: str, pedido: dict, provedor: str, politica: str, caso_demo: str | None = None) -> None:
    with _lock:
        c = con()
        t = agora()
        c.execute("INSERT INTO analises (id, criado_em, atualizado_em, status, origem, caso_demo, placa, provedor, politica, "
                  "pedido_json) VALUES (?,?,?,?,?,?,?,?,?,?)",
                  (aid, t, t, "processando", origem, caso_demo, (pedido.get("veiculo") or {}).get("placa"), provedor, politica,
                   json.dumps(pedido, ensure_ascii=False)))
        c.commit()


def concluir_analise(aid: str, resultado: dict, duracao: float) -> None:
    with _lock:
        c = con()
        placa = ((resultado.get("pedido_atpv") or {}).get("veiculo") or {}).get("placa")  # pode ter vindo só da ATPV-e
        c.execute("UPDATE analises SET status=?, atualizado_em=?, empresa=?, cnpj=?, veredito=?, faixa=?, indice=?, "
                  "resultado_json=?, duracao_s=?, placa=COALESCE(?, placa) WHERE id=?",
                  ("concluida", agora(), resultado["empresa"]["razao_social"], resultado["empresa"]["cnpj"], resultado["veredito"],
                   resultado["faixa"], resultado["indice"], json.dumps(resultado, ensure_ascii=False, default=str), duracao, placa,
                   aid))
        c.commit()


def falhar_analise(aid: str, erro: str) -> None:
    with _lock:
        con().execute("UPDATE analises SET status=?, atualizado_em=?, erro=? WHERE id=?", ("erro", agora(), erro, aid))
        con().commit()


def obter_analise(aid: str) -> dict | None:
    r = con().execute("SELECT * FROM analises WHERE id=?", (aid,)).fetchone()
    if not r:
        return None
    d = dict(r)
    d["pedido"] = json.loads(d.pop("pedido_json") or "{}")
    d["resultado"] = json.loads(d.pop("resultado_json") or "null")
    d["revisoes"] = [dict(x) for x in con().execute("SELECT * FROM revisoes WHERE analise_id=? ORDER BY id", (aid,))]
    return d


def listar_analises(limite: int = 100) -> list[dict]:
    q = ("SELECT id, criado_em, status, origem, caso_demo, empresa, placa, veredito, faixa, indice, provedor, politica, duracao_s, "
         "(SELECT decisao FROM revisoes r WHERE r.analise_id = a.id ORDER BY r.id DESC LIMIT 1) AS revisao "
         "FROM analises a ORDER BY criado_em DESC LIMIT ?")
    return [dict(r) for r in con().execute(q, (limite,))]


def registrar_revisao(aid: str, revisor: str, decisao: str, justificativa: str) -> dict:
    with _lock:
        c = con()
        c.execute("INSERT INTO revisoes (analise_id, criado_em, revisor, decisao, justificativa) VALUES (?,?,?,?,?)",
                  (aid, agora(), revisor, decisao, justificativa))
        c.commit()
    h = auditar("revisao_humana", aid, {"revisor": revisor, "decisao": decisao, "justificativa": justificativa},
                f"{revisor}: {decisao}")
    return {"ok": True, "hash": h}


def revisoes_rotuladas() -> list[dict]:
    """Casos revisados por humano viram rótulos para calibrar a faixa."""
    q = ("SELECT a.id, a.indice, a.veredito, r.decisao FROM revisoes r JOIN analises a ON a.id = r.analise_id "
         "WHERE r.id IN (SELECT MAX(id) FROM revisoes GROUP BY analise_id)")
    out = []
    for r in con().execute(q):
        esperado = "PODE" if r["decisao"] == "aprovar" else "NAO_PODE"
        out.append({"caso": r["id"], "indice": r["indice"], "previsto": r["veredito"], "esperado": esperado, "fonte": "revisao"})
    return out


def config_get(chave: str, padrao: Any = None) -> Any:
    r = con().execute("SELECT valor FROM config WHERE chave=?", (chave,)).fetchone()
    return json.loads(r["valor"]) if r else padrao


def config_set(chave: str, valor: Any) -> None:
    with _lock:
        con().execute("INSERT INTO config (chave, valor) VALUES (?, ?) ON CONFLICT(chave) DO UPDATE SET valor=excluded.valor",
                      (chave, json.dumps(valor, ensure_ascii=False)))
        con().commit()


def politica_atual() -> Politica:
    """Política vigente: o perfil salvo na tela de configuração (padrão: DETRAN-CE) com os ajustes gravados."""
    salvo = config_get("politica")
    base = Politica.por_nome((salvo or {}).get("perfil", "ce"))
    if salvo:
        for f in fields(Politica):
            if f.name in salvo and f.name not in ("nome", "uf"):
                v = salvo[f.name]
                setattr(base, f.name, Severidade(v) if isinstance(getattr(base, f.name), Severidade) else v)
    return base


# --------------------------------------------------------------------- leituras (reprocessamento)
def salvar_leituras(aid: str, leituras: list[LeituraDocumento]) -> None:
    pasta = DADOS / "analises" / aid
    pasta.mkdir(parents=True, exist_ok=True)
    dump = []
    for l in leituras:
        d = l.doc
        dump.append({
            "doc": {"id": d.id, "arquivo": d.arquivo, "nome": d.nome, "paginas": d.paginas, "sha256": d.sha256,
                    "metodo": d.metodo, "ocr_confianca": d.ocr_confianca},
            "classificacao": l.classificacao.model_dump(),
            **{k: getattr(l, k).model_dump() for k in ("partes", "regras", "ata", "procuracao", "substabelecimento", "revogacao", "crlv",
                                                        "atpv")
               if getattr(l, k) is not None},
            "consistencia": l.consistencia, "meta": l.meta,
        })
    (pasta / "leituras.json").write_text(json.dumps(dump, ensure_ascii=False, default=str), encoding="utf-8")


_MODELOS = {"partes": sc.ExtracaoPartes, "regras": sc.ExtracaoRegras, "ata": sc.ExtracaoAta, "procuracao": sc.ExtracaoProcuracao,
            "substabelecimento": sc.ExtracaoSubstabelecimento, "revogacao": sc.ExtracaoRevogacao, "crlv": sc.ExtracaoCRLV,
            "atpv": sc.ExtracaoATPV}


def carregar_leituras(aid: str) -> list[LeituraDocumento] | None:
    arq = DADOS / "analises" / aid / "leituras.json"
    if not arq.exists():
        return None
    out = []
    for item in json.loads(arq.read_text(encoding="utf-8")):
        dd = item["doc"]
        doc = Documento(dd["id"], dd["arquivo"], dd["nome"], dd["paginas"], dd["sha256"], dd["metodo"], dd["ocr_confianca"])
        doc.offsets = _calc_offsets(doc.paginas)
        l = LeituraDocumento(doc, sc.Classificacao.model_validate(item["classificacao"]))
        for k, m in _MODELOS.items():
            if k in item:
                setattr(l, k, m.model_validate(item[k]))
        l.consistencia = item.get("consistencia", {})
        l.meta = item.get("meta", {})
        out.append(l)
    return out
