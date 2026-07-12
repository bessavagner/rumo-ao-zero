"""Testes de `mapear_gatilhos` pós Task 7: o comando não usa mais o ORM (os models legados
`CravingEvent.gatilho_texto`, `Slip.gatilho_texto`, `IfThenPlan.gatilho_texto` e `EstadoInterno`
não existem mais no código). Em vez disso, construímos um banco SQLite LEGADO de mentira em
`tmp_path` — só com as colunas que o comando lê — e apontamos `--banco` para ele. Nada aqui toca
no banco do Django, então não precisa de `@pytest.mark.django_db`.
"""

import csv
import sqlite3

import pytest
from django.core.management import CommandError, call_command


def _linhas(caminho):
    with open(caminho, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _banco_legado(caminho, *, cravings=(), slips=(), ifthens=(), estados=(), juncoes=None):
    """Cria um SQLite com o schema legado mínimo que o comando espera.

    `estados` é uma lista de (id, nome). `juncoes` é um dict opcional
    {nome_da_tabela_de_juncao: [(estado_id, dono_id), ...]} — permite simular tanto o nome
    pós-rename (`log_cravingevent_estados_m2m`) quanto o legado (`log_cravingevent_estados`).
    """
    conn = sqlite3.connect(caminho)
    conn.execute("CREATE TABLE log_cravingevent (id INTEGER PRIMARY KEY, gatilho_texto TEXT)")
    conn.execute("CREATE TABLE log_slip (id INTEGER PRIMARY KEY, gatilho_texto TEXT)")
    conn.execute("CREATE TABLE baseline_ifthenplan (id INTEGER PRIMARY KEY, gatilho_texto TEXT)")
    conn.execute("CREATE TABLE baseline_estadointerno (id INTEGER PRIMARY KEY, nome TEXT)")

    conn.executemany("INSERT INTO log_cravingevent (gatilho_texto) VALUES (?)", [(t,) for t in cravings])
    conn.executemany("INSERT INTO log_slip (gatilho_texto) VALUES (?)", [(t,) for t in slips])
    conn.executemany("INSERT INTO baseline_ifthenplan (gatilho_texto) VALUES (?)", [(t,) for t in ifthens])
    conn.executemany("INSERT INTO baseline_estadointerno (id, nome) VALUES (?, ?)", list(estados))

    for tabela, linhas in (juncoes or {}).items():
        conn.execute(f"CREATE TABLE {tabela} (id INTEGER PRIMARY KEY, dono_id INTEGER, estadointerno_id INTEGER)")
        # `linhas` vem como [(estado_id, dono_id), ...] — mesma ordem usada nas chamadas abaixo.
        conn.executemany(
            f"INSERT INTO {tabela} (estadointerno_id, dono_id) VALUES (?, ?)", linhas
        )

    conn.commit()
    conn.close()


def test_mapeia_gatilhos_conta_ocorrencias_e_poe_nao_casados_no_topo(tmp_path):
    banco = tmp_path / "legado.sqlite3"
    _banco_legado(
        banco,
        cravings=["fim de expediente", "Fim do expediente", "fim de expediente"],
        slips=["xyzzy indecifrável"],
    )
    saida = tmp_path / "gatilhos.proposto.csv"

    call_command("mapear_gatilhos", "--banco", str(banco), "--alvo", "gatilhos", "--saida", str(saida))

    linhas = _linhas(saida)
    # Não casado no TOPO, marcado, com a célula `codigo` vazia para o humano preencher.
    assert linhas[0]["texto_original"] == "xyzzy indecifrável"
    assert linhas[0]["codigo"] == ""
    assert linhas[0]["regra"] == "SEM CORRESPONDENCIA"
    # As duas digitações de "fim de expediente" viram DUAS linhas (textos distintos) mas o mesmo
    # código — é exatamente o colapso que a migração vai aplicar.
    casados = {l["texto_original"]: l for l in linhas[1:]}
    assert casados["fim de expediente"]["codigo"] == "fim_expediente"
    assert casados["fim de expediente"]["ocorrencias"] == "2"
    assert casados["Fim do expediente"]["codigo"] == "fim_expediente"
    assert casados["Fim do expediente"]["ocorrencias"] == "1"


def test_mapeia_estados_colapsa_as_variacoes_reais(tmp_path):
    banco = tmp_path / "legado.sqlite3"
    _banco_legado(
        banco,
        estados=[(1, "cansaço"), (2, "cansado"), (3, "solidão"), (4, "solitário")],
    )
    saida = tmp_path / "estados.proposto.csv"

    call_command("mapear_gatilhos", "--banco", str(banco), "--alvo", "estados", "--saida", str(saida))

    codigos = {l["texto_original"]: l["codigo"] for l in _linhas(saida)}
    assert codigos == {
        "cansaço": "cansaco", "cansado": "cansaco",
        "solidão": "solidao", "solitário": "solidao",
    }


def test_mapeia_estados_soma_ocorrencias_das_tabelas_de_juncao_pos_rename(tmp_path):
    banco = tmp_path / "legado.sqlite3"
    _banco_legado(
        banco,
        estados=[(1, "cansaço"), (2, "solidão")],
        juncoes={
            "log_cravingevent_estados_m2m": [(1, 10), (1, 11), (2, 10)],
            "log_dailyentry_estados_m2m": [(1, 20)],
        },
    )
    saida = tmp_path / "estados.proposto.csv"

    call_command("mapear_gatilhos", "--banco", str(banco), "--alvo", "estados", "--saida", str(saida))

    ocorrencias = {l["texto_original"]: l["ocorrencias"] for l in _linhas(saida)}
    assert ocorrencias == {"cansaço": "3", "solidão": "1"}


def test_mapeia_estados_com_tabela_de_juncao_no_nome_legado_pre_rename(tmp_path):
    banco = tmp_path / "legado.sqlite3"
    _banco_legado(
        banco,
        estados=[(1, "fome")],
        juncoes={"log_cravingevent_estados": [(1, 10), (1, 11)]},
    )
    saida = tmp_path / "estados.proposto.csv"

    call_command("mapear_gatilhos", "--banco", str(banco), "--alvo", "estados", "--saida", str(saida))

    linhas = _linhas(saida)
    assert linhas[0]["texto_original"] == "fome"
    assert linhas[0]["ocorrencias"] == "2"


def test_mapeia_estados_sem_tabela_de_juncao_conta_um_uso_por_estado(tmp_path):
    banco = tmp_path / "legado.sqlite3"
    _banco_legado(banco, estados=[(1, "euforia")])
    saida = tmp_path / "estados.proposto.csv"

    call_command("mapear_gatilhos", "--banco", str(banco), "--alvo", "estados", "--saida", str(saida))

    linhas = _linhas(saida)
    assert linhas[0]["texto_original"] == "euforia"
    assert linhas[0]["ocorrencias"] == "1"


def test_banco_vazio_gera_csv_so_com_cabecalho(tmp_path):
    banco = tmp_path / "legado.sqlite3"
    _banco_legado(banco)
    saida = tmp_path / "vazio.csv"

    call_command("mapear_gatilhos", "--banco", str(banco), "--saida", str(saida))

    assert _linhas(saida) == []


def test_banco_sem_as_tabelas_esperadas_levanta_command_error(tmp_path):
    banco = tmp_path / "banco_qualquer.sqlite3"
    conn = sqlite3.connect(banco)
    conn.execute("CREATE TABLE alguma_coisa (id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()
    saida = tmp_path / "saida.csv"

    with pytest.raises(CommandError):
        call_command("mapear_gatilhos", "--banco", str(banco), "--alvo", "gatilhos", "--saida", str(saida))

    with pytest.raises(CommandError):
        call_command("mapear_gatilhos", "--banco", str(banco), "--alvo", "estados", "--saida", str(saida))
