"""Léxico jurídico determinístico — a "camada de conferência" da leitura generativa.

O LLM lê o documento e classifica; este módulo confere a classificação a partir das próprias
expressões que o LLM citou (e do texto original). Quando os dois discordam, a conclusão do léxico
prevalece nos pontos em que ele é confiável (forma de atuação, escopo do bem, poderes especiais,
substabelecimento) e a divergência vira um sinal de incerteza no score.

Medido na prática: o Qwen 27B local classificou "indistintamente" como assinatura CONJUNTA,
mesmo raciocinando — exatamente o tipo de erro que esta camada pega.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date

from unidecode import unidecode

MESES = {m: i for i, m in enumerate(
    ["janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
     "novembro", "dezembro"], start=1)}
NUMEROS = {"um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7,
           "oito": 8, "nove": 9, "dez": 10, "onze": 11, "doze": 12, "dezoito": 18, "vinte": 20, "vinte e quatro": 24,
           "trinta": 30, "sessenta": 60, "noventa": 90, "cento e vinte": 120, "cento e oitenta": 180}


def norm(s: str | None) -> str:
    """Minúsculas, sem acento, espaços colapsados — base de todas as comparações."""
    return re.sub(r"\s+", " ", unidecode(s or "").lower()).strip()


# ----------------------------------------------------------------------------- forma de atuação
_ISOLADO = [
    r"\bisoladamente\b", r"\bindistintamente\b", r"\bindividualmente\b", r"\bseparadamente\b",
    r"\bde per s[ie]\b", r"\bqualquer (um )?d[eo]s? (socios|administradores|diretores|outorgados|procuradores)\b",
    r"\bqualquer (um )?del[ae]s\b", r"\bum ou outro\b", r"\bcada um del[ae]s\b",
    r"\bem conjunto ou isoladamente\b", r"\bisolada ou conjuntamente\b", r"\bconjunta ou isoladamente\b",
    r"\bem conjunto ou separadamente\b", r"\bindependentemente (um do outro|da ordem de nomeacao)\b",
    r"\batuacao isolada\b", r"\bassinatura isolada\b", r"\bsozinh[oa]s?\b",
]
_CONJUNTO = [
    r"\bem conjunto\b", r"\bconjuntamente\b", r"\bassinatura conjunta\b", r"\bassinaturas conjuntas\b",
    r"\bassinatura de ambos\b", r"\bassinaturas de ambos\b", r"\bambos os (socios|administradores|diretores)\b",
    r"\bsempre juntos\b", r"\bduas assinaturas\b",
    r"\b(dois|2 \(dois\)|2) (administradores|diretores|socios|procuradores)\b",
]
# "isolada" negada (vedada a prática isolada, não podendo agir isoladamente) => conjunto
_NEGACAO_ISOLADO = re.compile(
    r"(vedad[ao]s?|proibid[ao]s?|nao (podendo|pode|poderao|poderá)|nunca|jamais|defeso)[^.;]{0,50}?\b(isolad|individual|separad)")
_PRECEDENCIA_ISOLADO = re.compile(
    r"em conjunto ou (isolada|separada)mente|isolada ou conjuntamente|conjunta ou isoladamente")


@dataclass
class SinalModo:
    modo: str | None  # "isolado" | "conjunto" | None (sem sinal)
    expressoes: list[str] = field(default_factory=list)
    certeza: float = 0.0  # 0..1


def modo_por_lexico(texto: str | None) -> SinalModo:
    """Forma de atuação (isolado/conjunto) inferida só pelas expressões do texto."""
    t = norm(texto)
    if not t:
        return SinalModo(None)
    if _PRECEDENCIA_ISOLADO.search(t):
        return SinalModo("isolado", [_PRECEDENCIA_ISOLADO.search(t).group(0)], 0.95)
    neg = _NEGACAO_ISOLADO.search(t)
    iso = [m.group(0) for p in _ISOLADO for m in re.finditer(p, t)]
    con = [m.group(0) for p in _CONJUNTO for m in re.finditer(p, t)]
    if neg:
        return SinalModo("conjunto", [neg.group(0)] + con, 0.9)
    if iso and not con:
        return SinalModo("isolado", iso, 0.95)
    if con and not iso:
        return SinalModo("conjunto", con, 0.9)
    if iso and con:
        return SinalModo(None, iso + con, 0.3)  # misto/ambíguo: deixa para o LLM + revisão
    return SinalModo(None)


_QTD = re.compile(r"\b(\d+)\s*(?:\((?:um|uma|dois|duas|tres|quatro)\))?\s*(diretor|diretores|administrador|administradores|"
                  r"socios|procurador|procuradores)\b|\b(dois|duas|tres)\s+(diretores|administradores|socios|procuradores)\b")


_QTD_DE = re.compile(r"\b(\d+|um|uma|dois|duas|tres)\s*(?:\([a-z]+\))?\s+(?:dos|das|dentre os|dentre as|entre os|de seus|de suas)\s+"
                     r"(?:\d+|tres|quatro|cinco)?\s*(?:\([a-z]+\))?\s*(diretor|administrador|socio)")


def quantidade_por_lexico(texto: str | None) -> int | None:
    """'assinatura de 2 (dois) Diretores' -> 2; 'quaisquer dois dos três administradores' -> 2 (N de M: vale N)."""
    t = norm(texto)
    m = _QTD_DE.search(t)
    if m:
        n = m.group(1)
        return int(n) if n.isdigit() else NUMEROS.get(n)
    m = _QTD.search(t)
    if not m:
        return None
    n = m.group(1) or m.group(3)
    return int(n) if n.isdigit() else NUMEROS.get(n)


# procurador que só age junto com outro: precisa estar nos PODERES ("em conjunto com um Diretor")
CONJUNTO_COM = re.compile(r"(em conjunto|conjuntamente|juntamente)\s+com\s+(?:um|uma|qualquer|o|a|os|as)?\s*(?:dos|das|de seus)?\s*"
                          r"(diretor|administrador|socio)")


# --------------------------------------------------------------------------------- escopo do bem
_VEICULO = re.compile(r"\b(veicul|automove|automotor|frota\b|caminh(ao|oes)|motociclet|utilitari)")
_IMOVEL = re.compile(r"\b(imove(is|l)|bens de raiz|bem de raiz)\b")
_IMOBILIZADO = re.compile(r"\bativo (imobilizado|permanente|nao circulante)\b")
_MOVEIS = re.compile(r"\bbens moveis\b")
_ALIENACAO = re.compile(r"\b(aliena|alienar|vend|transfer|ced(er|ido)|cessao|dispor|disposicao)")
_ONERACAO = re.compile(r"\b(onera|gravar|hipotec|penhor|garantia real)")
_PROCURACAO = re.compile(r"\b(procurac|mandat[aá]ri|constituir procurador)")


# negação de poderes dirigida a pessoas: "não lhes cabendo poderes de administração", "sem poderes de representação"
NEGA_PODERES = re.compile(
    r"nao lhes? cab|sem (quaisquer )?poderes|nao (tem|terao|possuem|possui|tera) (quaisquer )?poderes|"
    r"nao (podera|poderao|pode|podem) (representar|administrar|assinar|usar o nome)|exclusivamente (na qualidade de|como) quotist|"
    r"apenas (na qualidade de|como) quotist|vedad[ao] (a eles|aos socios quotistas)")


# ato de ADQUIRIR (lado comprador) e de assumir obrigações
AQUISICAO = re.compile(r"\b(adquirir|adquira|aquisicao|aquisicoes|comprar|compra de|compras de)\b")
OBRIGACOES = re.compile(r"\b(contrair|assumir|assuncao de)\b[^.;]{0,40}\b(obrigac|divida|emprestimo|financiamento)|"
                        r"\b(emprestimos?|financiamentos?)\b|"
                        r"\b(criem|crie|criar|gerem|gere|importem|importe|impliquem|implique|envolvam)\b[^.;]{0,30}\b"
                        r"(obrigac|responsabilidade)")
# poder de procurador para COMPRAR veículo ("na qualidade de adquirente" conta; "transferir ao adquirente" não)
ADQUIRIR_PODER = re.compile(r"\b(comprar|adquirir|adquira)\b|\bcompra\s+de\s+veicul|\baquisicao\s+de\s+veicul|"
                            r"\bna\s+qualidade\s+de\s+(adquirente|compradora?)\b|\bcomo\s+(adquirente|compradora?)\b|"
                            r"\brepresentar\b[^.;]{0,60}\bna\s+compra\b")


def atos_da_regra(escopo: str, texto: str | None) -> tuple[set[str], int | None]:
    """A qual ato a regra se aplica (alienar = vender; adquirir = comprar) e a especialidade dela na compra.
    Corrige leituras em que a IA rotula uma regra de COMPRA como 'alienação' (ou 'outro')."""
    t = norm(texto)
    aq, al, ob = bool(AQUISICAO.search(t)), bool(_ALIENACAO.search(t)), bool(OBRIGACOES.search(t))
    veic, imob, moveis = bool(_VEICULO.search(t)), bool(_IMOBILIZADO.search(t)), bool(_MOVEIS.search(t))
    nivel = 3 if veic else 2 if (imob or moveis) else 1
    if escopo == "geral":
        return {"alienar", "adquirir"}, 0
    if escopo in ("alienacao_bens_imoveis", "outorgar_procuracoes"):
        return ({"alienar"} if not aq else set()), None
    if aq and not al:              # cláusula só de aquisição (mesmo que a IA tenha posto 'alienacao_*')
        return {"adquirir"}, nivel
    if aq and al:                  # "comprar, vender e alienar veículos"
        return {"alienar", "adquirir"}, nivel
    if ob and al:                  # "documentos que criem obrigações ou importem alienação de bens": vale para os dois
        return {"alienar", "adquirir"}, 1
    if ob and escopo in ("outro", "obrigacoes_garantias", "geral"):
        return {"adquirir"}, 1    # assumir obrigação acima de X alcança a compra (o preço é obrigação)
    return {"alienar"}, None


# cláusula geral de administração ("a administração da sociedade caberá a ..., com representação ativa e passiva ...,
# inclusive a venda de bens"): a venda aparece como exemplo; a regra é a geral de representação (vale para comprar)
_ADMIN_GERAL = re.compile(r"\badministracao da (sociedade|empresa|companhia|cooperativa|associacao)\b|"
                          r"\brepresentacao ativa e passiva\b|\bativa e passivamente\b|\bem juizo (ou|e) fora dele\b|"
                          r"\bplenos poderes de (gestao|administracao)\b")


def clausula_geral_de_administracao(texto: str | None) -> bool:
    return bool(_ADMIN_GERAL.search(norm(texto)))


# cargos nomeados em estatutos (cooperativas, associações, S.A.): "o Presidente em conjunto com o Tesoureiro"
_CARGOS = ("presidente", "vice-presidente", "vice presidente", "tesoureiro", "tesoureira", "secretario", "secretaria",
           "diretor", "diretora", "superintendente", "gerente geral", "conselheiro", "provedor", "coordenador")


def e_cargo(texto: str | None) -> bool:
    """'Presidente', 'Diretor Financeiro', '1º Tesoureiro' (sem sobrenome de pessoa)."""
    t = norm(texto).replace("1o ", "").replace("2o ", "").strip(" .")
    if not t or len(t.split()) > 4:
        return False
    return any(t == c or t.startswith(c + " ") or t.startswith(c + "-") for c in _CARGOS) and not re.search(r"\b[a-z]{3,}\s+[a-z]{3,}\s+[a-z]{3,}\s+[a-z]{3,}", t)


def cargo_casa(cargo_regra: str, cargo_pessoa: str | None) -> bool:
    """O cargo exigido na regra ('Diretor Financeiro') corresponde ao cargo da pessoa ('Diretora Financeira')?"""
    def raizes(x):
        return [w[:6] for w in norm(x).replace("-", " ").split() if w not in ("de", "da", "do", "o", "a", "1o", "2o")]
    rr, rp = raizes(cargo_regra), raizes(cargo_pessoa or "")
    qualificadores = {"vice", "adjunt", "suplen", "substi", "segund", "interi"}
    if any(any(p.startswith(q) for q in qualificadores) for p in rp) and not any(
            any(r.startswith(q) for q in qualificadores) for r in rr):
        return False  # "Vice-Presidente" não é "Presidente"
    return bool(rr) and all(any(p.startswith(r[:5]) for p in rp) for r in rr)


# órgãos que fiscalizam ou aconselham, mas não representam (CC, arts. 1.066–1.070; LSA, arts. 161–165; Lei 5.764, art. 56)
_SEM_REPRESENTACAO = re.compile(r"\bfiscal\b|\bfiscais\b|\bsuplente|conselho (consultivo|deliberativo|de etica)")


def cargo_sem_representacao(cargo: str | None) -> bool:
    return bool(_SEM_REPRESENTACAO.search(norm(cargo)))


# cargo nomeado como QUEM representa/assina: "Compete ao Presidente representar...", "representada pelo
# Diretor-Presidente", "assinados pelo Diretor-Presidente em conjunto com o Diretor Financeiro"
_OFICIO = (r"(diretor[a]?[ -]presidente|vice[ -]presidente|presidente|superintendente|provedor[a]?|tesoureir[oa]|"
           r"secretari[oa][ -]geral|secretari[oa]|diretor[a]?[ -](?:executiv|geral|financeir|administrativ|comercial|"
           r"tecnic|operacional)[oa]?)")
_SUJEITO = [re.compile(p) for p in (
    r"\b(?:compete|cabe|cabera|incumbe|competira|caber)\s+(?:ao|a)\s+" + _OFICIO + r"\b[^.;]{0,30}?\brepresent",
    r"\brepresentad[ao]s?\b[^.;]{0,120}?\bpel[oa]\s+" + _OFICIO + r"\b",
    r"\bassinad[oa]s?\b[^.;]{0,60}?\bpel[oa]\s+" + _OFICIO + r"\b",
    r"\b(?:o|a)\s+" + _OFICIO + r"\s+(?:representara|representa|assinara|assina)\b",
)]
_EM_CONJUNTO = r"\s*,?\s*(?:em conjunto com|juntamente com|conjuntamente com|e)\s+(?:o|a)\s+" + _OFICIO + r"\b"
_SUBSTITUTO = re.compile(r"(ausencia|ausencias|impediment|substitu|vacancia|falta)[^.;]{0,60}$")


def _rotulo_cargo(c: str) -> str:
    return "-".join(" ".join(w.capitalize() for w in parte.split(" ")) for parte in c.split("-"))


_SUBST_CARGO = [re.compile(p) for p in (
    r"\b(?:ausencias?|impedimentos?|faltas?|vacancia|licencas?)\b[^.;]{0,90}?\b(?:o|a|pelo|pela|ao)\s+" + _OFICIO + r"\b",
    r"\bsubstituid[oa]s?\b[^.;]{0,40}?\bpel[oa]\s+" + _OFICIO + r"\b",
    r"\b(?:o|a)\s+" + _OFICIO + r"\s+(?:o |a )?substitu",
)]


def cargos_substitutos(texto: str | None) -> list[str]:
    """Cargos que só representam no lugar do titular ('na ausência ou impedimento do Presidente, o Vice-Presidente').
    O sistema não tem como provar a ausência: quem assina nessa condição vai para revisão humana."""
    t = norm(texto)
    out = []
    for rx in _SUBST_CARGO:
        for m in rx.finditer(t):
            c = _rotulo_cargo(m.group(1))
            ctx = t[max(0, m.start() - 10):m.end()]
            titular = re.search(r"\b(?:do|da)\s+" + _OFICIO + r"\b", ctx)  # "ausência DO Presidente": o titular não é substituto
            if titular and _rotulo_cargo(titular.group(1)) == c:
                continue
            if c not in out:
                out.append(c)
    return out


def cargos_signatarios(texto: str | None) -> list[str]:
    """Cargos que a cláusula nomeia como quem representa/assina (o principal e quem assina 'em conjunto com' ele).
    Quem só substitui 'na ausência ou impedimento' não entra."""
    t = norm(texto)
    for rx in _SUJEITO:
        for m in rx.finditer(t):
            if _SUBSTITUTO.search(t[max(0, m.start() - 70):m.start()]):
                continue
            cargos = [m.group(1)]
            seg = re.match(_EM_CONJUNTO, t[m.end():])
            if seg:
                cargos.append(seg.group(1))
            return [_rotulo_cargo(c) for c in cargos]
    return []


@dataclass
class SinalEscopo:
    menciona_veiculo: bool
    menciona_imovel: bool
    menciona_imobilizado: bool
    menciona_bens_moveis: bool
    alienacao: bool
    oneracao: bool
    procuracao: bool

    @property
    def so_imoveis(self) -> bool:
        """Regra que fala de imóveis e de nada que alcance veículo (armadilha semântica clássica)."""
        return self.menciona_imovel and not (self.menciona_veiculo or self.menciona_imobilizado or self.menciona_bens_moveis)


def escopo_por_lexico(texto: str | None) -> SinalEscopo:
    t = norm(texto)
    return SinalEscopo(
        menciona_veiculo=bool(_VEICULO.search(t)), menciona_imovel=bool(_IMOVEL.search(t)),
        menciona_imobilizado=bool(_IMOBILIZADO.search(t)), menciona_bens_moveis=bool(_MOVEIS.search(t)),
        alienacao=bool(_ALIENACAO.search(t)), oneracao=bool(_ONERACAO.search(t)), procuracao=bool(_PROCURACAO.search(t)),
    )


# --------------------------------------------------------------------------- poderes (procuração)
_ALIENAR = re.compile(r"\b(vender|vende-l|alienar|alienacao|transferir|transferencia de propriedade|ceder|compromissar|"
                      r"prometer vender|dispor)\b")
_ATPV = re.compile(r"\b(atpv(-?e)?|autorizacao para transferencia|crv\b|certificado de registro de veiculo|"
                   r"recibo de compra e venda|documento unico de transferencia|\bdut\b)")
_ESPECIAIS = re.compile(r"\b(poderes especiais|especiais e expressos|expressos e especiais|poderes especificos|"
                        r"especialmente para|para o fim especial|para o fim especifico)\b")
_GERAIS = re.compile(r"\b(amplos e gerais poderes|amplos poderes|gerais poderes|poderes gerais|gerir e administrar|"
                     r"administracao geral|administracao ordinaria|ad negotia)\b")
_NEGA_ALIENAR = re.compile(r"(vedad[ao]|exceto|salvo|nao (incluid|compreend|abrang))[^.;]{0,60}(vend|aliena|transfer)")


@dataclass
class SinalPoderes:
    alienar: bool
    atpv: bool
    especiais: bool
    gerais: bool
    alienacao_negada: bool


def poderes_por_lexico(texto: str | None) -> SinalPoderes:
    t = norm(texto)
    return SinalPoderes(alienar=bool(_ALIENAR.search(t)), atpv=bool(_ATPV.search(t)), especiais=bool(_ESPECIAIS.search(t)),
                        gerais=bool(_GERAIS.search(t)), alienacao_negada=bool(_NEGA_ALIENAR.search(t)))


# ---------------------------------------------------------------------------- substabelecimento
def substabelecimento_por_lexico(texto: str | None) -> str | None:
    t = norm(texto)
    if not t:
        return None
    if re.search(r"(vedad[oa]|proibid[oa]|defeso)[^.;]{0,30}substabelec|substabelecimento[^.;]{0,20}(vedad|proibid)|"
                 r"sem (direito|poderes?|faculdade) (a|de|para) substabelecer|nao (podendo|pode|podera) substabelecer|"
                 r"nao (sendo )?(permitid|admitid)[oa][^.;]{0,20}substabelec", t):
        return "vedado"
    if "substabelec" in t:
        if "sem reserva" in t:
            return "permitido_sem_reserva"
        if "com reserva" in t:
            return "permitido_com_reserva"
        return "permitido"
    return None


def reserva_por_lexico(texto: str | None) -> str | None:
    t = norm(texto)
    if re.search(r"\bsem (a )?reserva\b", t):
        return "sem_reserva"
    if re.search(r"\bcom (a )?reserva\b", t):
        return "com_reserva"
    return None


# ------------------------------------------------------------- classes/grupos de administradores
# "um Administrador A e um Administrador B", "quotas classe B": exige combinação ENTRE grupos — o schema genérico
# ("dois em conjunto") perde essa restrição, então o caso vai para revisão. Letra MAIÚSCULA: evita "administrador a quem".
_CLASSES = re.compile(r"(?i:administrador(?:es|a|as)?|diretor(?:es|a|as)?|s[oó]cios?|quotas?|classe|categoria|grupo)\s+"
                      r"(?:(?i:da|de|do)\s+)?(?:(?i:classe|categoria|grupo)\s+)?[A-D]\b(?![a-zà-ú])")


def menciona_classes(texto: str | None) -> bool:
    return bool(_CLASSES.search(texto or ""))


_ALTERACAO_CITADA = re.compile(r"\b(primeira|segunda|terceira|quarta|quinta|sexta|setima|oitava|nona|decima)\s+altera|"
                               r"\baltera[cç][aã]o\s+(?:contratual\s+)?n[ºo°.]?\s*(\d+)")
_ORDINAIS = {"primeira": 1, "segunda": 2, "terceira": 3, "quarta": 4, "quinta": 5, "sexta": 6, "setima": 7, "oitava": 8,
             "nona": 9, "decima": 10}


def alteracoes_citadas(texto: str | None) -> set[int]:
    """Números de alterações contratuais citadas num texto ("nos termos da Terceira Alteração", "alteração nº 4")."""
    out = set()
    for m in _ALTERACAO_CITADA.finditer(norm(texto)):
        if m.group(1):
            out.add(_ORDINAIS[m.group(1)])
        elif m.group(2):
            out.add(int(m.group(2)))
    return out


# ------------------------------------------------------------------------------- revogações
_REVOGA_ATO = re.compile(r"\b(revoga|revogam|revogando|revogou|revogaram|ficam? revogad[ao]s?|ficam? cancelad[ao]s?|"
                         r"tornam? sem efeito|torna-se sem efeito)\b[^.;]{0,160}?\bprocura")
_REVOGA_NEGADO = re.compile(r"(podera|poderao|pode|podem|salvo|ate a|ate que|sem prejuizo|nao se considera)[^.;]{0,25}$")
_REVOGA_TODAS = re.compile(r"\b(todas|quaisquer|todos os mandatos|todas e quaisquer)\b[^.;]{0,40}\bprocura")


@dataclass
class SinalRevogacao:
    trecho: str
    todas: bool


def revogacoes_no_texto(texto: str | None) -> list[SinalRevogacao]:
    """Atos de revogação de procuração DENTRO de outros documentos ("revogando a procuração anterior",
    "ficam revogadas todas as procurações..."), ignorando "poderá ser revogada", "até revogação" etc."""
    t = norm(texto)
    out = []
    for m in _REVOGA_ATO.finditer(t):
        antes = t[max(0, m.start() - 40):m.start()]
        if _REVOGA_NEGADO.search(antes):
            continue
        ini = max(t.rfind(". ", 0, m.start()), t.rfind("; ", 0, m.start()))
        fim = t.find(".", m.end())
        frase = t[ini + 2 if ini >= 0 else 0: fim if fim > 0 else m.end() + 200]
        out.append(SinalRevogacao(frase.strip(), bool(_REVOGA_TODAS.search(frase))))
    return out


# ------------------------------------------------------------------------------------- datas
def parse_data(texto: str | None) -> date | None:
    """Aceita AAAA-MM-DD, DD/MM/AAAA e '10 de dezembro de 2026' / '1º de março de 2025'."""
    if not texto:
        return None
    t = norm(texto)
    if m := re.search(r"(\d{4})-(\d{2})-(\d{2})", t):
        y, mo, d = map(int, m.groups())
    elif m := re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", t):
        d, mo, y = map(int, m.groups())
    elif m := re.search(r"(\d{1,2})o? de ([a-z]+) de (\d{4})", t):
        d, mo, y = int(m.group(1)), MESES.get(m.group(2)), int(m.group(3))
        if not mo:
            return None
    else:
        return None
    try:
        return date(y, mo, d)
    except ValueError:
        return None


def _numero(token: str) -> int | None:
    token = token.strip()
    if token.isdigit():
        return int(token)
    return NUMEROS.get(token)


def prazo_em_dias(texto: str | None) -> int | None:
    """'pelo prazo de 6 (seis) meses' -> 182; '1 (um) ano' -> 365; '90 (noventa) dias' -> 90."""
    t = norm(texto)
    m = re.search(r"(\d+|[a-z]+(?: e [a-z]+)?)\s*(?:\(([a-z ]+)\))?\s*(dias?|mes(?:es)?|anos?)\b", t)
    if not m:
        return None
    n = _numero(m.group(1)) or (_numero(m.group(2)) if m.group(2) else None)
    if not n:
        return None
    unidade = m.group(3)
    return n if unidade.startswith("dia") else n * 30 + n // 2 if unidade.startswith("mes") else n * 365


def somar_prazo(inicio: date, texto: str | None) -> date | None:
    """Data final de um prazo contado a partir de `inicio` (meses/anos pelo calendário civil)."""
    t = norm(texto)
    m = re.search(r"(\d+|[a-z]+(?: e [a-z]+)?)\s*(?:\(([a-z ]+)\))?\s*(dias?|mes(?:es)?|anos?)\b", t)
    if not m:
        return None
    n = _numero(m.group(1)) or (_numero(m.group(2)) if m.group(2) else None)
    if not n:
        return None
    u = m.group(3)
    from datetime import timedelta
    if u.startswith("dia"):
        return inicio + timedelta(days=n)
    meses = n if u.startswith("mes") else 12 * n
    y, mo = divmod(inicio.month - 1 + meses, 12)
    ano, mes = inicio.year + y, mo + 1
    import calendar
    dia = min(inicio.day, calendar.monthrange(ano, mes)[1])
    return date(ano, mes, dia)


def valor_monetario(texto: str | None) -> float | None:
    """'R$ 150.000,00 (cento e cinquenta mil reais)' -> 150000.0"""
    m = re.search(r"R\$\s*([\d.]+(?:,\d{2})?)", texto or "")
    if not m:
        return None
    return float(m.group(1).replace(".", "").replace(",", "."))
