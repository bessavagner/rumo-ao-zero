import csv

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils import timezone

User = get_user_model()


def _linhas(caminho):
    with open(caminho, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


@pytest.mark.django_db
def test_mapeia_gatilhos_conta_ocorrencias_e_poe_nao_casados_no_topo(tmp_path):
    from apps.log.models import CravingEvent, Slip

    user = User.objects.create_user(username="map", password="x")
    for texto in ["fim de expediente", "Fim do expediente", "fim de expediente"]:
        CravingEvent.objects.create(
            user=user, timestamp=timezone.now(), substancia="tabaco",
            intensidade_pico=7, gatilho_texto=texto, gatilho="outro",
        )
    Slip.objects.create(
        user=user, timestamp=timezone.now(), substancia="alcool",
        gatilho_texto="xyzzy indecifrável", gatilho="outro",
    )
    saida = tmp_path / "gatilhos.proposto.csv"

    call_command("mapear_gatilhos", "--alvo", "gatilhos", "--saida", str(saida))

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


@pytest.mark.django_db
def test_mapeia_estados_colapsa_as_variacoes_reais(tmp_path):
    from apps.baseline.models import EstadoInterno

    user = User.objects.create_user(username="map", password="x")
    for nome in ["cansaço", "cansado", "solidão", "solitário"]:
        EstadoInterno.objects.create(user=user, nome=nome)
    saida = tmp_path / "estados.proposto.csv"

    call_command("mapear_gatilhos", "--alvo", "estados", "--saida", str(saida))

    codigos = {l["texto_original"]: l["codigo"] for l in _linhas(saida)}
    assert codigos == {
        "cansaço": "cansaco", "cansado": "cansaco",
        "solidão": "solidao", "solitário": "solidao",
    }


@pytest.mark.django_db
def test_banco_vazio_gera_csv_so_com_cabecalho(tmp_path):
    saida = tmp_path / "vazio.csv"
    call_command("mapear_gatilhos", "--saida", str(saida))
    assert _linhas(saida) == []
