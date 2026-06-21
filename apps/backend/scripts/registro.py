#!/usr/bin/env python3
"""Registro de capturas (DIÁRIO / CRAVING / SLIP / PULSO) via API — CLI no host.

Camada fina de CLI sobre `registro_core` (a MESMA lógica que o servidor MCP `mcp_server.py`
usa). Este script é o fallback humano pro Bessa rodar na mão; o bot do WhatsApp usa os tools
MCP. O core faz auth + resolve nomes -> IDs (get-or-create) + POST. Aqui só parseamos argumentos
e imprimimos JSON.

Sem dependências externas (stdlib). Lê credenciais de ../.secrets/dev.env.

Exemplos:
    python3 registro.py daily --data 2026-06-12 --humor 3 --energia 4 \\
        --sono-h 7 --sono-q 4 --craving-pico 2 --estado cansaço \\
        --linha "primeiro dia, ansioso mas firme" --boa "aguentei a tarde"

    python3 registro.py craving --data 2026-06-15 --hora 17:10 --substancia tabaco \\
        --intensidade-pico 8 --gatilho "tarde sozinho, estresse" \\
        --estado solidão --estado cansaço --fiz "andar 15 min" --fiz-categoria movimento \\
        --tempo-baixar-3 18 --aprendizado "o gatilho é o tédio das 17h"

    python3 registro.py slip --data 2026-06-20 --hora 21:30 --substancia alcool \\
        --quantidade "2 cervejas" --contexto "churrasco de família" \\
        --gatilho "frustração com discussão" --aprendizado "gatilho é frustração silenciosa"

    python3 registro.py pulso --data 2026-06-22 --hora 16:00 --humor 2 --energia 2 \\
        --estado tédio --nota "bateu uma fossa no fim da tarde"

Saída (stdout): JSON. Código de saída 0 = ok; !=0 = faltou campo obrigatório ou erro da API.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from registro_core import (  # noqa: E402
    SUBSTITUICAO_CATEGORIAS,
    Api,
    RegistroError,
    registrar_craving,
    registrar_diario,
    registrar_pulso,
    registrar_slip,
    editar_gatilho,
    resolve_estado,
    resolve_substituicao,
    resolve_trigger,
)


def emit_ok(payload: dict) -> None:
    print(json.dumps({"ok": True, **payload}, ensure_ascii=False))
    sys.exit(0)


# ------------------------------------------------------------------------- comandos

def cmd_daily(api: Api, a: argparse.Namespace) -> None:
    emit_ok(registrar_diario(
        api, data=a.data, humor=a.humor, energia=a.energia, sono_h=a.sono_h, sono_q=a.sono_q,
        craving_pico=a.craving_pico, estados=a.estado, linhas=a.linha,
        corpo=a.corpo, boa=a.boa, dificil=a.dificil,
    ))


def cmd_craving(api: Api, a: argparse.Namespace) -> None:
    emit_ok(registrar_craving(
        api, data=a.data, hora=a.hora, substancia=a.substancia,
        intensidade_pico=a.intensidade_pico, gatilho=a.gatilho, estados=a.estado,
        fiz=a.fiz, fiz_categoria=a.fiz_categoria, duracao_min=a.duracao_min,
        intensidade_final=a.intensidade_final, tempo_baixar_3=a.tempo_baixar_3,
        aprendizado=a.aprendizado,
    ))


def cmd_slip(api: Api, a: argparse.Namespace) -> None:
    emit_ok(registrar_slip(
        api, data=a.data, hora=a.hora, substancia=a.substancia, quantidade=a.quantidade,
        contexto=a.contexto, gatilho=a.gatilho, aprendizado=a.aprendizado,
        reset_alcool=a.reset_alcool, reset_tabaco=a.reset_tabaco,
    ))


def cmd_pulso(api: Api, a: argparse.Namespace) -> None:
    emit_ok(registrar_pulso(
        api, data=a.data, hora=a.hora, humor=a.humor, energia=a.energia,
        craving=a.craving, estados=a.estado, nota=a.nota,
    ))


def cmd_trigger_upsert(api: Api, a: argparse.Namespace) -> None:
    tid, novo = resolve_trigger(api, a.nome, a.contexto or "")
    emit_ok({"tipo": "TRIGGER", "id": tid, "criado": novo, "nome": a.nome})


def cmd_gatilho_editar(api: Api, a: argparse.Namespace) -> None:
    emit_ok(editar_gatilho(
        api, gatilho=a.gatilho, id=a.id, novo_nome=a.novo_nome, contexto=a.contexto,
        emocao_precedente=a.emocao_precedente, estado_mais_comum=a.estado_mais_comum,
        frequencia_semana=a.frequencia_semana, ativo=a.ativo,
    ))


def cmd_sub_upsert(api: Api, a: argparse.Namespace) -> None:
    sid, novo = resolve_substituicao(api, a.nome, a.categoria)
    emit_ok({"tipo": "SUBSTITUICAO", "id": sid, "criado": novo, "nome": a.nome})


def cmd_estado_upsert(api: Api, a: argparse.Namespace) -> None:
    eid, novo = resolve_estado(api, a.nome)
    emit_ok({"tipo": "ESTADO", "id": eid, "criado": novo, "nome": a.nome})


# ----------------------------------------------------------------------------- cli

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Registra capturas (DIÁRIO/CRAVING/SLIP/PULSO) via API.")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("daily", help="DIÁRIO — 1x/dia")
    d.add_argument("--data", required=True, help="YYYY-MM-DD ou DD/MM")
    d.add_argument("--humor", type=int, required=True, help="0–10")
    d.add_argument("--energia", type=int, required=True, help="0–10")
    d.add_argument("--sono-h", dest="sono_h", required=True, help="horas, ex 7 ou 7.5")
    d.add_argument("--sono-q", dest="sono_q", type=int, required=True, help="qualidade 0–10")
    d.add_argument("--craving-pico", dest="craving_pico", type=int, default=None, help="0–10")
    d.add_argument("--estado", action="append", help="estado interno (repetível)")
    d.add_argument("--linha", action="append", help="linha de prosa (até 3, repetível)")
    d.add_argument("--corpo", help="algo do corpo")
    d.add_argument("--boa", help="coisa boa")
    d.add_argument("--dificil", help="coisa difícil")
    d.set_defaults(func=cmd_daily)

    c = sub.add_parser("craving", help="CRAVING — episódio ≥6/10")
    c.add_argument("--data", required=True, help="YYYY-MM-DD ou DD/MM")
    c.add_argument("--hora", required=True, help="HH:MM")
    c.add_argument("--substancia", required=True, choices=["alcool", "tabaco", "ambos"])
    c.add_argument("--intensidade-pico", dest="intensidade_pico", type=int, required=True, help="0–10")
    c.add_argument("--gatilho", required=True, help="gatilho/contexto (vira Trigger)")
    c.add_argument("--estado", action="append", help="estado interno (repetível)")
    c.add_argument("--fiz", help="o que fez (vira Substitution)")
    c.add_argument("--fiz-categoria", dest="fiz_categoria", choices=SUBSTITUICAO_CATEGORIAS,
                   help="categoria da substituição (se nova)")
    c.add_argument("--duracao-min", dest="duracao_min", type=int, default=None)
    c.add_argument("--intensidade-final", dest="intensidade_final", type=int, default=None, help="0–10")
    c.add_argument("--tempo-baixar-3", dest="tempo_baixar_3", type=int, default=None, help="min até ≤3")
    c.add_argument("--aprendizado")
    c.set_defaults(func=cmd_craving)

    s = sub.add_parser("slip", help="SLIP — dado, sem julgamento")
    s.add_argument("--data", required=True, help="YYYY-MM-DD ou DD/MM")
    s.add_argument("--hora", required=True, help="HH:MM")
    s.add_argument("--substancia", required=True, choices=["alcool", "tabaco"])
    s.add_argument("--quantidade", help="ex: 2 cervejas")
    s.add_argument("--contexto")
    s.add_argument("--gatilho", help="gatilho/contexto (vira Trigger)")
    s.add_argument("--aprendizado")
    s.add_argument("--reset-alcool", dest="reset_alcool", action="store_true")
    s.add_argument("--reset-tabaco", dest="reset_tabaco", action="store_true")
    s.set_defaults(func=cmd_slip)

    pu = sub.add_parser("pulso", help="PULSO — check-in de humor/energia ao longo do dia")
    pu.add_argument("--data", required=True, help="YYYY-MM-DD ou DD/MM")
    pu.add_argument("--hora", required=True, help="HH:MM")
    pu.add_argument("--humor", type=int, required=True, help="0–10")
    pu.add_argument("--energia", type=int, required=True, help="0–10")
    pu.add_argument("--craving", type=int, default=None, help="0–10")
    pu.add_argument("--estado", action="append", help="estado interno (repetível)")
    pu.add_argument("--nota", help="observação curta do momento")
    pu.set_defaults(func=cmd_pulso)

    t = sub.add_parser("trigger-upsert", help="get-or-create Trigger por nome")
    t.add_argument("--nome", required=True)
    t.add_argument("--contexto")
    t.set_defaults(func=cmd_trigger_upsert)

    ge = sub.add_parser("gatilho-editar", help="edita um Trigger existente (por nome ou --id)")
    ge.add_argument("--gatilho", help="nome do gatilho a editar (case-insensitive)")
    ge.add_argument("--id", type=int, default=None, help="id do gatilho (use se o nome for ambíguo)")
    ge.add_argument("--novo-nome", dest="novo_nome", help="renomeia o gatilho")
    ge.add_argument("--contexto")
    ge.add_argument("--emocao-precedente", dest="emocao_precedente")
    ge.add_argument("--estado-mais-comum", dest="estado_mais_comum",
                    help="nome de estado interno (get-or-create); '' desvincula")
    ge.add_argument("--frequencia-semana", dest="frequencia_semana", type=int, default=None)
    ge.add_argument("--ativo", action=argparse.BooleanOptionalAction, default=None,
                    help="--ativo / --no-ativo (arquiva sem apagar)")
    ge.set_defaults(func=cmd_gatilho_editar)

    su = sub.add_parser("sub-upsert", help="get-or-create Substitution por nome")
    su.add_argument("--nome", required=True)
    su.add_argument("--categoria", choices=SUBSTITUICAO_CATEGORIAS)
    su.set_defaults(func=cmd_sub_upsert)

    e = sub.add_parser("estado-upsert", help="get-or-create EstadoInterno por nome")
    e.add_argument("--nome", required=True)
    e.set_defaults(func=cmd_estado_upsert)

    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        api = Api.connect()
        args.func(api, args)
    except RegistroError as exc:
        payload: dict = {"ok": False, "erro": str(exc)}
        if exc.detalhe is not None:
            payload["detalhe"] = exc.detalhe
        print(json.dumps(payload, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
