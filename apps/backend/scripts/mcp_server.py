#!/usr/bin/env python3
"""Servidor MCP "rumo-registro" — superfície de tools p/ o OpenClaw registrar SEM shell.

O agente do WhatsApp roda com tools.profile=messaging, que NÃO expõe exec/read (por segurança).
Então, em vez de rodar `registro.py` via shell, ele chama estes tools MCP estruturados. O
OpenClaw é cliente MCP nativo e o perfil messaging permite tools de MCP. Decisão: ADR D-003.

Camada fina sobre `registro_core` — a MESMA lógica do CLI `registro.py` (auth, get-or-create,
POST). Aqui só expomos como tools e adicionamos consultar/editar/apagar/referencia_api.

Roda via stdio (o gateway do OpenClaw o lança como subprocesso). Depende de `mcp` (no venv
~/.venvs/rumo-mcp) + stdlib (via registro_core). Lê credenciais de ../.secrets/dev.env.

Registrar no OpenClaw (uma vez):
    openclaw mcp add rumo-registro \
      --command /home/bessa/.venvs/rumo-mcp/bin/python \
      --arg /home/bessa/Documents/projetos/rumo_ao_zero/apps/backend/scripts/mcp_server.py
"""

from __future__ import annotations

import os
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP  # noqa: E402

import registro_core as core  # noqa: E402
from registro_core import Api, RegistroError  # noqa: E402

mcp = FastMCP("rumo-registro")

_REFERENCIA_PATH = (
    Path(__file__).resolve().parents[3]
    / "docs/.ai/reports/005_captura_mobile/openclaw_skill/rumo-ao-zero/references/api-reference.md"
)

_state: dict = {"api": None}


def _api() -> Api:
    """Conexão (token) preguiçosa e cacheada no processo."""
    if _state["api"] is None:
        _state["api"] = Api.connect()
    return _state["api"]


def _err(exc: Exception) -> dict:
    payload: dict = {"ok": False, "erro": str(exc)}
    detalhe = getattr(exc, "detalhe", None)
    if detalhe is not None:
        payload["detalhe"] = detalhe
    return payload


# --------------------------------------------------------------------------- tools de escrita

@mcp.tool()
def registrar_pulso(
    data: str, hora: str, humor: int, energia: int, craving: int | None = None,
    estados: list[str] | None = None, nota: str | None = None,
) -> dict:
    """Registra um PULSO — check-in de humor/energia AO LONGO DO DIA (vários por dia).

    data: 'YYYY-MM-DD' ou 'DD/MM'. hora: 'HH:MM'. humor/energia: 1–5.
    craving: intensidade da fissura no momento, 0–10 (opcional; default 0).
    estados: nomes de estados internos (ex-HALT: fome/raiva/solidão/cansaço/…), get-or-create.
    nota: observação curta do momento.
    """
    try:
        return {"ok": True, **core.registrar_pulso(
            _api(), data=data, hora=hora, humor=humor, energia=energia, craving=craving,
            estados=estados, nota=nota)}
    except Exception as exc:  # noqa: BLE001 - vira erro estruturado pro modelo
        return _err(exc)


@mcp.tool()
def registrar_diario(
    data: str, humor: int, energia: int, sono_h: float, sono_q: int,
    craving_pico: int | None = None, estados: list[str] | None = None,
    linhas: list[str] | None = None, corpo: str | None = None,
    boa: str | None = None, dificil: str | None = None,
) -> dict:
    """Registra o DIÁRIO — balanço reflexivo de fim de dia (1×/dia; repetir a data dá erro 400).

    Obrigatórios: data, humor (1–5), energia (1–5), sono_h (horas, ex 7.5), sono_q (1–5).
    Opcionais: craving_pico (0–10), estados (get-or-create), linhas (até 3), corpo, boa, dificil.
    """
    try:
        return {"ok": True, **core.registrar_diario(
            _api(), data=data, humor=humor, energia=energia, sono_h=sono_h, sono_q=sono_q,
            craving_pico=craving_pico, estados=estados, linhas=linhas, corpo=corpo, boa=boa,
            dificil=dificil)}
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


@mcp.tool()
def registrar_craving(
    data: str, hora: str, substancia: str, intensidade_pico: int, gatilho: str,
    estados: list[str] | None = None, fiz: str | None = None, fiz_categoria: str | None = None,
    duracao_min: int | None = None, intensidade_final: int | None = None,
    tempo_baixar_3: int | None = None, aprendizado: str | None = None,
) -> dict:
    """Registra um CRAVING (fissura ≥6/10).

    substancia: 'alcool' | 'tabaco' | 'ambos'. intensidade_pico: 0–10.
    gatilho: vira/liga um Trigger (get-or-create). fiz: vira/liga uma Substitution
    (se NOVA, exige fiz_categoria ∈ oral/movimento/social/cognitivo/ambiental).
    """
    try:
        return {"ok": True, **core.registrar_craving(
            _api(), data=data, hora=hora, substancia=substancia, intensidade_pico=intensidade_pico,
            gatilho=gatilho, estados=estados, fiz=fiz, fiz_categoria=fiz_categoria,
            duracao_min=duracao_min, intensidade_final=intensidade_final,
            tempo_baixar_3=tempo_baixar_3, aprendizado=aprendizado)}
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


@mcp.tool()
def registrar_slip(
    data: str, hora: str, substancia: str,
    quantidade: str | None = None, contexto: str | None = None, gatilho: str | None = None,
    aprendizado: str | None = None, reset_alcool: bool = False, reset_tabaco: bool = False,
) -> dict:
    """Registra um SLIP (recaída — DADO, sem julgamento).

    substancia: 'alcool' | 'tabaco' (slip não aceita 'ambos').
    gatilho: vira/liga um Trigger (get-or-create). reset_*: zera o streak da substância.
    """
    try:
        return {"ok": True, **core.registrar_slip(
            _api(), data=data, hora=hora, substancia=substancia, quantidade=quantidade,
            contexto=contexto, gatilho=gatilho, aprendizado=aprendizado,
            reset_alcool=reset_alcool, reset_tabaco=reset_tabaco)}
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


@mcp.tool()
def editar_gatilho(
    gatilho: str | None = None, id: int | None = None,
    novo_nome: str | None = None, contexto: str | None = None,
    emocao_precedente: str | None = None, estado_mais_comum: str | None = None,
    frequencia_semana: int | None = None, ativo: bool | None = None,
) -> dict:
    """Edita um GATILHO (Trigger) existente no mapa de gatilhos — corrigir/enriquecer/arquivar.

    Identifique por `gatilho` (nome, busca case-insensitive) OU `id` (use o id se o nome
    for ambíguo). Só envia os campos informados; os demais ficam intactos.
    Campos: novo_nome (renomeia), contexto (texto), emocao_precedente, estado_mais_comum
    (nome de um estado interno, get-or-create; ''=desvincula), frequencia_semana (0+),
    ativo (false p/ arquivar sem apagar o histórico de cravings/slips ligados).
    Pra DESCOBRIR/listar gatilhos antes de editar: consultar('baseline/triggers').
    """
    try:
        return {"ok": True, **core.editar_gatilho(
            _api(), gatilho=gatilho, id=id, novo_nome=novo_nome, contexto=contexto,
            emocao_precedente=emocao_precedente, estado_mais_comum=estado_mais_comum,
            frequencia_semana=frequencia_semana, ativo=ativo)}
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


# --------------------------------------------------------- tools de leitura/edição (MCP-only)

_RECURSOS_LOG = {"daily", "cravings", "slips", "pulsos"}
_RECURSOS_OUTROS = {
    "baseline/profile", "baseline/values", "baseline/triggers", "baseline/estados",
    "baseline/substitutions", "baseline/ifthen",
    "backlog/items", "backlog/decisions", "backlog/consultas", "backlog/compras",
}


def _path_recurso(recurso: str) -> str:
    r = recurso.strip("/")
    if r in _RECURSOS_LOG:
        r = f"log/{r}"
    if r not in {f"log/{x}" for x in _RECURSOS_LOG} and r not in _RECURSOS_OUTROS:
        raise RegistroError(
            f"recurso desconhecido '{recurso}'. Use ex.: pulsos, cravings, daily, slips, "
            "baseline/estados, backlog/items"
        )
    return f"/api/{r}/"


@mcp.tool()
def consultar(recurso: str, filtros: dict | None = None) -> dict:
    """Consulta (GET) registros já gravados — para responder 'quantos cravings essa semana?' etc.

    recurso: ex. 'pulsos', 'cravings', 'daily', 'slips', 'baseline/estados', 'backlog/items'.
    filtros: querystring, ex. {'ordering': '-timestamp', 'substancia': 'alcool', 'page': 1}.
    Resposta paginada: {count, next, previous, results}.
    """
    try:
        path = _path_recurso(recurso)
        if filtros:
            path = f"{path}?{urllib.parse.urlencode(filtros)}"
        return {"ok": True, "resultado": _api().get(path)}
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


@mcp.tool()
def editar(recurso: str, id: int, campos: dict) -> dict:
    """Edita (PATCH parcial) um registro existente. Ex.: corrigir o humor de um diário.

    recurso: ex. 'daily', 'pulsos', 'cravings', 'slips'. id: o id do registro. campos: o que mudar.
    """
    try:
        path = f"{_path_recurso(recurso)}{int(id)}/"
        return {"ok": True, "atualizado": _api().patch(path, campos)}
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


@mcp.tool()
def apagar(recurso: str, id: int) -> dict:
    """Apaga (DELETE) um registro existente. Use com cuidado; é irreversível."""
    try:
        path = f"{_path_recurso(recurso)}{int(id)}/"
        _api().delete(path)
        return {"ok": True, "apagado": {"recurso": recurso, "id": int(id)}}
    except Exception as exc:  # noqa: BLE001
        return _err(exc)


@mcp.tool()
def referencia_api() -> dict:
    """Retorna a referência COMPLETA da API (markdown) — endpoints, campos, validações, filtros.

    Use quando o Bessa pedir detalhes da API que vão além das descrições dos outros tools
    (ex.: todos os campos de um recurso, o que a API não expõe, como paginar/filtrar).
    """
    try:
        return {"ok": True, "referencia_markdown": _REFERENCIA_PATH.read_text(encoding="utf-8")}
    except OSError as exc:
        return _err(RegistroError(f"não consegui ler a referência em {_REFERENCIA_PATH}: {exc}"))


if __name__ == "__main__":
    mcp.run()
