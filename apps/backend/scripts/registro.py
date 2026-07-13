#!/usr/bin/env python3
"""Registro de capturas (DIÁRIO / CRAVING / SLIP / PULSO) via API — CLI no host.

Camada fina de CLI sobre `registro_core` (a MESMA lógica que o servidor MCP `mcp_server.py`
usa). Este script é o fallback humano pro Bessa rodar na mão; o bot do WhatsApp usa os tools
MCP. O core faz auth + POST; `gatilho`/`estado` são CÓDIGOS da taxonomia fixa (ver subcomando
`taxonomia`), não texto livre. Aqui só parseamos argumentos e imprimimos JSON.

Sem dependências externas (stdlib). Lê credenciais de ../.secrets/dev.env.

Exemplos:
    python3 registro.py daily --data 2026-06-12 --humor 3 --energia 4 \\
        --sono-h 7 --sono-q 4 --craving-pico 2 --estado cansaco \\
        --linha "primeiro dia, ansioso mas firme" --boa "aguentei a tarde"

    python3 registro.py craving --data 2026-06-15 --hora 17:10 --substancia tabaco \\
        --intensidade-pico 8 --gatilho tedio_vazio --detalhes "tarde sozinho, estresse" \\
        --estado solidao --estado cansaco --substituicao movimento --substituicao-detalhes "corri 5k" \\
        --tempo-baixar-3 18 --aprendizado "o gatilho é o tédio das 17h"

    python3 registro.py slip --data 2026-06-20 --hora 21:30 --substancia alcool \\
        --quantidade "2 cervejas" --contexto "churrasco de família" \\
        --gatilho discussao_atrito --detalhes "frustração com discussão" \\
        --aprendizado "gatilho é frustração silenciosa"

    python3 registro.py pulso --data 2026-06-22 --hora 16:00 --humor 2 --energia 2 \\
        --estado tedio --nota "bateu uma fossa no fim da tarde"

    python3 registro.py taxonomia

Saída (stdout): JSON. Código de saída 0 = ok; !=0 = faltou campo obrigatório ou erro da API.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from registro_core import (  # noqa: E402
    Api,
    RegistroError,
    registrar_craving,
    registrar_diario,
    registrar_pulso,
    registrar_slip,
    taxonomia,
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
        intensidade_pico=a.intensidade_pico, gatilho=a.gatilho,
        gatilhos_adicionais=a.gatilho_adicional, detalhes=a.detalhes, estados=a.estado,
        substituicao=a.substituicao, substituicao_detalhes=a.substituicao_detalhes,
        duracao_min=a.duracao_min,
        intensidade_final=a.intensidade_final, tempo_baixar_3=a.tempo_baixar_3,
        aprendizado=a.aprendizado,
    ))


def cmd_slip(api: Api, a: argparse.Namespace) -> None:
    emit_ok(registrar_slip(
        api, data=a.data, hora=a.hora, substancia=a.substancia, gatilho=a.gatilho,
        gatilhos_adicionais=a.gatilho_adicional, detalhes=a.detalhes, quantidade=a.quantidade,
        contexto=a.contexto, aprendizado=a.aprendizado,
        reset_alcool=a.reset_alcool, reset_tabaco=a.reset_tabaco,
    ))


def cmd_pulso(api: Api, a: argparse.Namespace) -> None:
    emit_ok(registrar_pulso(
        api, data=a.data, hora=a.hora, humor=a.humor, energia=a.energia,
        craving=a.craving, estados=a.estado, nota=a.nota,
    ))


def cmd_taxonomia(api: Api, a: argparse.Namespace) -> None:
    emit_ok(taxonomia(api))


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
    d.add_argument("--estado", action="append", help="código de estado interno (repetível)")
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
    c.add_argument("--gatilho", required=True, help="código da situação (ver: registro.py taxonomia)")
    c.add_argument("--gatilho-adicional", dest="gatilho_adicional", action="append",
                   help="código de situação adicional (repetível)")
    c.add_argument("--detalhes", help="a fala inteira, em texto livre")
    c.add_argument("--estado", action="append", help="código de estado interno (repetível)")
    c.add_argument("--substituicao", choices=["oral", "movimento", "social", "cognitivo", "ambiental"],
                   help="código da substituição usada (ver: registro.py taxonomia)")
    c.add_argument("--substituicao-detalhes", dest="substituicao_detalhes",
                   help="a fala inteira do que fez, em texto livre")
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
    s.add_argument("--gatilho", required=True, help="código da situação (ver: registro.py taxonomia)")
    s.add_argument("--gatilho-adicional", dest="gatilho_adicional", action="append",
                   help="código de situação adicional (repetível)")
    s.add_argument("--detalhes", help="a fala inteira, em texto livre")
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
    pu.add_argument("--estado", action="append", help="código de estado interno (repetível)")
    pu.add_argument("--nota", help="observação curta do momento")
    pu.set_defaults(func=cmd_pulso)

    sub.add_parser("taxonomia", help="lista os códigos válidos de gatilho/estado/substituição").set_defaults(
        func=cmd_taxonomia
    )

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
