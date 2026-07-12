from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.baseline.models import BaselineProfile, Substitution
from apps.log.models import CravingEvent, DailyEntry, Pulso, Slip

User = get_user_model()


def _user_com_baseline(data_zero, custo_mensal="300.00"):
    user = User.objects.create_user(username="api", password="x")
    BaselineProfile.objects.create(
        user=user, data_zero=data_zero, custo_mensal_estimado=custo_mensal
    )
    return user


@pytest.mark.django_db
def test_dashboard_exige_autenticacao():
    client = APIClient()
    resp = client.get("/api/dashboard/")
    assert resp.status_code in (401, 403)


@pytest.mark.django_db
def test_dashboard_streaks_e_dinheiro():
    data_zero = date.today() - timedelta(days=10)
    user = _user_com_baseline(data_zero, custo_mensal="300.00")
    client = APIClient()
    client.force_authenticate(user=user)

    resp = client.get("/api/dashboard/")

    assert resp.status_code == 200, resp.content
    data = resp.json()
    assert data["dias_ate_dia1"] == 0
    assert data["streaks"]["alcool"]["consecutivo"] == 10
    assert data["streaks"]["tabaco"]["consecutivo"] == 10
    assert data["dinheiro_economizado"] == pytest.approx(100.0)
    assert "estados_frequencia" in data
    assert "triggers_frequencia" in data
    assert "substituicoes_eficacia" in data


@pytest.mark.django_db
def test_dashboard_escopa_por_user():
    data_zero = date.today() - timedelta(days=5)
    user = _user_com_baseline(data_zero)
    outro = User.objects.create_user(username="outro", password="x")
    BaselineProfile.objects.create(user=outro, data_zero=data_zero, custo_mensal_estimado="0")
    Slip.objects.create(user=outro, timestamp=f"{date.today()}T12:00:00Z", substancia="alcool")
    client = APIClient()
    client.force_authenticate(user=user)

    resp = client.get("/api/dashboard/")
    assert resp.json()["streaks"]["alcool"]["consecutivo"] == 5


@pytest.mark.django_db
def test_series_humor_junta_pulsos_e_dailies_ordenado():
    user = _user_com_baseline(date.today() - timedelta(days=3))
    Pulso.objects.create(
        user=user, timestamp="2026-06-22T10:00:00Z", humor=4, energia=4, craving=2
    )
    DailyEntry.objects.create(
        user=user, data="2026-06-21", humor=3, energia=3, sono_h="7.0",
        sono_q=4, craving_pico=5,
    )
    client = APIClient()
    client.force_authenticate(user=user)

    resp = client.get("/api/series/humor/?dias=3650")

    assert resp.status_code == 200, resp.content
    data = resp.json()
    pontos = data["pontos"]
    assert len(pontos) == 2
    assert pontos[0]["tipo"] == "daily"
    assert pontos[0]["humor"] == 3
    assert pontos[0]["craving"] == 5
    assert pontos[1]["tipo"] == "pulso"
    assert pontos[1]["craving"] == 2


@pytest.mark.django_db
def test_series_humor_exige_autenticacao():
    client = APIClient()
    assert client.get("/api/series/humor/").status_code in (401, 403)


@pytest.mark.django_db
def test_dashboard_respeita_a_janela_e_a_devolve():
    """O rótulo 'da semana' precisa poder ser verdade: o front pede ?dias=7 e recebe 7."""
    user = _user_com_baseline(date.today() - timedelta(days=60))
    antigo = date.today() - timedelta(days=20)
    CravingEvent.objects.create(
        user=user, timestamp=f"{antigo}T12:00:00Z", substancia="tabaco",
        intensidade_pico=7, gatilho="tedio_vazio",
    )
    CravingEvent.objects.create(
        user=user, timestamp=f"{date.today()}T12:00:00Z", substancia="tabaco",
        intensidade_pico=8, gatilho="fim_expediente",
    )
    client = APIClient()
    client.force_authenticate(user=user)

    semana = client.get("/api/dashboard/?dias=7").json()
    mes = client.get("/api/dashboard/").json()

    assert semana["dias"] == 7
    assert [b["situacao"] for b in semana["triggers_frequencia"]["por_situacao"]] == ["fim_expediente"]
    assert mes["dias"] == 30
    assert len(mes["triggers_frequencia"]["por_situacao"]) == 2


@pytest.mark.django_db
def test_dashboard_dias_invalido_cai_no_default():
    user = _user_com_baseline(date.today() - timedelta(days=5))
    client = APIClient()
    client.force_authenticate(user=user)
    assert client.get("/api/dashboard/?dias=abacaxi").json()["dias"] == 30


@pytest.mark.django_db
def test_dashboard_traz_os_tres_cortes_de_gatilho():
    user = _user_com_baseline(date.today() - timedelta(days=5))
    CravingEvent.objects.create(
        user=user, timestamp=f"{date.today()}T12:00:00Z", substancia="tabaco",
        intensidade_pico=8, gatilho="fim_expediente", gatilhos_adicionais=["bebendo"],
    )
    client = APIClient()
    client.force_authenticate(user=user)

    cortes = client.get("/api/dashboard/").json()["triggers_frequencia"]

    assert cortes["por_situacao"][0]["rotulo"] == "Fim de expediente"
    assert cortes["por_categoria"][0]["categoria"] == "urges_tentacoes"
    assert cortes["coocorrencia"][0]["adicional"] == "bebendo"
