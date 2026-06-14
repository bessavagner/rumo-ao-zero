from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.baseline.models import BaselineProfile, Substitution
from apps.log.models import CravingEvent, Slip

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
