"""Taxonomia fixa de gatilhos e estados internos — fonte única de verdade.

As 8 categorias são a taxonomia de recaída de Marlatt & Gordon (1985), operacionalizada por
Annis no IDS (álcool) e no ISS (tabaco) — os mesmos 8 fatores servem as duas substâncias, que
é exatamente o caso deste projeto (cessação simultânea).

A **situação** é o que o usuário escolhe (concreta, na linguagem dele). A **categoria** é
derivada por dicionário e NUNCA é armazenada — assim não pode divergir. Não existe caminho de
código que crie uma situação nova: mudar a lista é mudar este arquivo.

Importado por: models (choices + validators), API da taxonomia, services (agregação),
comando `mapear_gatilhos` e data migrations.
"""

from __future__ import annotations

import csv
import unicodedata
from pathlib import Path

MAPAS_DIR = Path(__file__).resolve().parent / "mapas"

# ── Categorias clínicas (IDS/ISS) ────────────────────────────────────────────
CATEGORIAS: list[tuple[str, str]] = [
    ("emocoes_desagradaveis", "Emoções desagradáveis"),
    ("urges_tentacoes", "Urges e tentações"),
    ("desconforto_fisico", "Desconforto físico"),
    ("emocoes_agradaveis", "Emoções agradáveis"),
    ("conflito_outros", "Conflito com outros"),
    ("pressao_social", "Pressão social"),
    ("momentos_agradaveis_outros", "Momentos agradáveis com outros"),
    ("testar_controle", "Testar o controle"),
]

# (codigo, rotulo, categoria | None). A ORDEM é a ordem do <select> no app.
# "outro" é a única sem categoria: é rede de segurança da migração e válvula de escape. Se virar
# a barra mais alta do dashboard, a taxonomia está errada e esta lista deve ser revisada.
_SITUACOES: list[tuple[str, str, str | None]] = [
    ("frustracao_trabalho", "Frustração no trabalho", "emocoes_desagradaveis"),
    ("ansiedade_estresse", "Ansiedade / estresse", "emocoes_desagradaveis"),
    ("tedio_vazio", "Tédio / vazio", "emocoes_desagradaveis"),
    ("tristeza_solidao", "Tristeza / solidão", "emocoes_desagradaveis"),
    # Fim de expediente é gatilho de HORÁRIO/ritual (o corpo pede no mesmo horário, independente
    # de como o dia foi) — por isso urge, não emoção desagradável.
    ("fim_expediente", "Fim de expediente", "urges_tentacoes"),
    # "Bebendo" é gatilho de primeira classe: a condição cruzada ("só fumo se beber") é o eixo
    # do projeto e não pode ficar escondida em texto livre.
    ("bebendo", "Bebendo (gatilho cruzado)", "urges_tentacoes"),
    ("apos_refeicao", "Após refeição", "urges_tentacoes"),
    ("cafe_pausa", "Café / pausa", "urges_tentacoes"),
    ("cansaco_noite_mal_dormida", "Cansaço / noite mal dormida", "desconforto_fisico"),
    ("dor_mal_estar", "Dor / mal-estar", "desconforto_fisico"),
    ("comemoracao", "Comemoração / boa notícia", "emocoes_agradaveis"),
    ("relaxar_recompensa", "Relaxar, me recompensar", "emocoes_agradaveis"),
    ("discussao_atrito", "Discussão / atrito", "conflito_outros"),
    ("evento_social", "Evento social (bar, churrasco)", "pressao_social"),
    ("alguem_ofereceu", "Alguém me ofereceu", "pressao_social"),
    ("bom_momento_proximos", "Bom momento com gente próxima", "momentos_agradaveis_outros"),
    ("testar_um_so", "Testar se consigo parar em um", "testar_controle"),
    ("outro", "Outro", None),
]

SITUACOES: list[tuple[str, str]] = [(c, r) for c, r, _ in _SITUACOES]
SITUACAO_CATEGORIA: dict[str, str] = {c: cat for c, _, cat in _SITUACOES if cat}
_ROTULO_SITUACAO: dict[str, str] = dict(SITUACOES)
_ROTULO_CATEGORIA: dict[str, str] = dict(CATEGORIAS)
CODIGOS_SITUACAO = frozenset(_ROTULO_SITUACAO)

# ── Estados internos (ex-HALT) ───────────────────────────────────────────────
# Os 4 do HALT + os que já apareceram nos dados reais. Lista plana: estado não tem categoria.
ESTADOS: list[tuple[str, str]] = [
    ("fome", "Fome"),
    ("raiva", "Raiva"),
    ("solidao", "Solidão"),
    ("cansaco", "Cansaço"),
    ("ansiedade", "Ansiedade"),
    ("tedio", "Tédio"),
    ("frustracao", "Frustração"),
    ("tristeza", "Tristeza"),
    ("sobrecarga", "Sobrecarga"),
    ("euforia", "Euforia"),
    ("outro", "Outro"),
]
_ROTULO_ESTADO: dict[str, str] = dict(ESTADOS)
CODIGOS_ESTADO = frozenset(_ROTULO_ESTADO)


# ── Derivação ────────────────────────────────────────────────────────────────
def categoria_de(situacao: str | None) -> str | None:
    """Categoria clínica da situação. None para 'outro' e para código desconhecido."""
    return SITUACAO_CATEGORIA.get(situacao or "")


def rotulo_situacao(codigo: str) -> str:
    return _ROTULO_SITUACAO.get(codigo, codigo)


def rotulo_categoria(codigo: str) -> str:
    return _ROTULO_CATEGORIA.get(codigo, codigo)


def rotulo_estado(codigo: str) -> str:
    return _ROTULO_ESTADO.get(codigo, codigo)


def grupos_gatilhos() -> dict:
    """Payload de `GET /api/taxonomia/gatilhos/` — pronto para virar <optgroup> no front."""
    grupos = []
    for cat, rotulo in CATEGORIAS:
        situacoes = [
            {"codigo": c, "rotulo": r} for c, r, cat_c in _SITUACOES if cat_c == cat
        ]
        grupos.append({"categoria": cat, "rotulo": rotulo, "situacoes": situacoes})
    sem_categoria = [{"codigo": c, "rotulo": r} for c, r, cat_c in _SITUACOES if cat_c is None]
    return {"grupos": grupos, "sem_categoria": sem_categoria}


def lista_estados() -> list[dict]:
    """Payload de `GET /api/taxonomia/estados/`."""
    return [{"codigo": c, "rotulo": r} for c, r in ESTADOS]


# ── Normalização e classificação por palavra-chave ───────────────────────────
def normalizar(texto: str) -> str:
    """Minúsculas, sem acento, espaços colapsados — para casar 'Cansaço' com 'cansaco'."""
    sem_acento = "".join(
        ch for ch in unicodedata.normalize("NFD", texto or "")
        if unicodedata.category(ch) != "Mn"
    )
    return " ".join(sem_acento.lower().split())


# Primeira regra que casar vence — por isso a ORDEM importa: 'fim de expediente' antes de
# 'trabalho', senão todo fim de expediente viraria frustração no trabalho.
REGRAS_GATILHO: list[tuple[str, list[str]]] = [
    ("fim_expediente", ["fim de expediente", "fim do expediente", "saida do trabalho",
                        "fim de tarde", "fim do dia", "17h"]),
    ("bebendo", ["bebendo", "bebi", "cerveja", "birita", "drink", "whisky", "vinho"]),
    ("discussao_atrito", ["discussao", "discuti", "briga", "brigamos", "atrito",
                          "bati de frente", "bateu de frente"]),
    ("frustracao_trabalho", ["frustracao", "frustrado", "frustrante", "chefe", "reuniao",
                             "deadline", "trabalho", "decepcao", "desvalorizado",
                             "desvalorizado"]),
    ("ansiedade_estresse", ["ansiedade", "ansioso", "estresse", "estressado", "nervoso"]),
    ("tedio_vazio", ["tedio", "entediado", "vazio", "sem nada pra fazer"]),
    # Ciúmes não tem situação própria: por decisão do Bessa entra em tristeza/solidão (é o
    # registro de emoção desagradável mais próximo do que ele descreve).
    ("tristeza_solidao", ["tristeza", "triste", "solidao", "sozinho", "solitario",
                          "ciumes", "ciume"]),
    ("apos_refeicao", ["apos refeicao", "depois de comer", "depois do almoco", "pos almoco",
                       "almoco", "jantar"]),
    ("cafe_pausa", ["cafe", "pausa", "cafezinho"]),
    ("cansaco_noite_mal_dormida", ["cansaco", "cansado", "exausto", "mal dormida", "nao dormi",
                                   "sono ruim"]),
    ("dor_mal_estar", ["dor de", "dor ", "mal estar", "mal-estar", "doente", "ressaca"]),
    # Euforia e "produtiv" são gatilhos positivos e caem aqui (reforço positivo, no IDS).
    ("comemoracao", ["comemoracao", "comemorar", "comemorando", "boa noticia", "vitoria",
                     "euforia", "euforico", "produtiv"]),
    ("relaxar_recompensa", ["relaxar", "recompensa", "merecia", "me premiar"]),
    ("evento_social", ["churrasco", "bar", "festa", "aniversario", "evento"]),
    ("alguem_ofereceu", ["ofereceu", "ofereceram", "me oferecer"]),
    ("bom_momento_proximos", ["bom momento", "amigos", "familia", "gente proxima"]),
    ("testar_um_so", ["so um", "um so", "parar em um", "testar se consigo"]),
]

REGRAS_ESTADO: list[tuple[str, list[str]]] = [
    ("fome", ["fome", "faminto"]),
    ("raiva", ["raiva", "irritado", "puto", "bravo"]),
    ("solidao", ["solidao", "solitario", "sozinho"]),
    ("cansaco", ["cansaco", "cansado", "exausto", "esgotado", "sonolento", "sono"]),
    ("ansiedade", ["ansiedade", "ansioso", "nervoso", "preocupado", "preocupacao"]),
    ("tedio", ["tedio", "entediado"]),
    ("frustracao", ["frustracao", "frustrado"]),
    ("tristeza", ["tristeza", "triste", "pra baixo"]),
    ("sobrecarga", ["sobrecarga", "sobrecarregado", "estresse", "estressado"]),
    ("euforia", ["euforia", "euforico", "animado", "satisfacao", "satisfeito"]),
]


def _classificar(texto: str, regras: list[tuple[str, list[str]]]) -> tuple[str | None, str | None]:
    alvo = normalizar(texto)
    if not alvo:
        return None, None
    for codigo, palavras in regras:
        for palavra in palavras:
            if palavra in alvo:
                return codigo, palavra
    return None, None


def classificar_gatilho(texto: str) -> tuple[str | None, str | None]:
    """(situacao, palavra_que_casou) ou (None, None). Só sugere — quem decide é o humano."""
    return _classificar(texto, REGRAS_GATILHO)


def classificar_estado(texto: str) -> tuple[str | None, str | None]:
    return _classificar(texto, REGRAS_ESTADO)


# ── Mapa aprovado (versionado no repo, lido pelas data migrations) ───────────
def carregar_mapa(nome: str) -> dict[str, str]:
    """Lê `mapas/<nome>.csv` (colunas: texto_original, ocorrencias, codigo, regra).

    Devolve {texto_normalizado: codigo}. Arquivo ausente ou célula `codigo` vazia não é erro:
    o texto vira 'outro' na migração e o original é preservado em `detalhes`.
    """
    caminho = MAPAS_DIR / f"{nome}.csv"
    if not caminho.exists():
        return {}
    mapa: dict[str, str] = {}
    with caminho.open(encoding="utf-8", newline="") as f:
        for linha in csv.DictReader(f):
            codigo = (linha.get("codigo") or "").strip()
            texto = normalizar(linha.get("texto_original") or "")
            if texto and codigo:
                mapa[texto] = codigo
    return mapa


# ── Validators (usados pelos JSONFields; o DRF os herda do model e devolve 400) ───
def _valida_codigos(valor, permitidos: frozenset[str], nome: str) -> None:
    from django.core.exceptions import ValidationError

    if not isinstance(valor, list):
        raise ValidationError(f"{nome}: esperava uma lista de códigos.")
    # `not isinstance(c, str)` primeiro: um elemento dict/list não é hasheável e `in permitidos`
    # estouraria TypeError (500) em vez de devolver 400 — a curto-circuito do `or` evita isso.
    desconhecidos = [c for c in valor if not isinstance(c, str) or c not in permitidos]
    if desconhecidos:
        raise ValidationError(
            f"{nome}: código(s) fora da taxonomia: {', '.join(map(str, desconhecidos))}."
        )


def valida_situacoes(valor) -> None:
    _valida_codigos(valor, CODIGOS_SITUACAO, "gatilhos_adicionais")


def valida_estados(valor) -> None:
    _valida_codigos(valor, CODIGOS_ESTADO, "estados")
