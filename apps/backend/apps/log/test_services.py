from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.baseline.models import BaselineProfile
from apps.log.models import Slip
from apps.log.services import (
    dias_ate_dia1,
    dinheiro_economizado,
    streak_consecutivo,
    streak_cumulativo_ano,
    substituicoes_eficacia,
)

User = get_user_model()


def _user_com_baseline(username, dias_desde_zero, custo_mensal=0):
    user = User.objects.create_user(username=username, password="x")
    BaselineProfile.objects.create(
        user=user,
        data_zero=date.today() - timedelta(days=dias_desde_zero),
        custo_mensal_estimado=custo_mensal,
    )
    return user


@pytest.mark.django_db
class TestStreak:
    def test_sem_slip_retorna_dias_desde_baseline(self):
        user = _user_com_baseline("a", 10)
        assert streak_consecutivo(user, "alcool") == 10

    def test_com_slip_recente_retorna_dias_desde_slip(self):
        user = _user_com_baseline("b", 30)
        Slip.objects.create(
            user=user,
            substancia="alcool",
            timestamp=timezone.now() - timedelta(days=5),
            aprendizado="t",
        )
        assert streak_consecutivo(user, "alcool") == 5

    def test_cumulativo_nao_zera_com_slip(self):
        # baseline no dia 1 do ano para isolar o cálculo do ano
        user = User.objects.create_user(username="c", password="x")
        BaselineProfile.objects.create(user=user, data_zero=date(date.today().year, 1, 1))
        Slip.objects.create(
            user=user,
            substancia="alcool",
            timestamp=timezone.now() - timedelta(days=5),
            aprendizado="t",
        )
        dias_ano = (date.today() - date(date.today().year, 1, 1)).days + 1
        assert streak_cumulativo_ano(user, "alcool") == dias_ano - 1


@pytest.mark.django_db
def test_dinheiro_economizado():
    user = _user_com_baseline("d", 30, custo_mensal=300)
    assert dinheiro_economizado(user) == pytest.approx(300.0)


@pytest.mark.django_db
def test_data_zero_no_futuro_zera_streak_e_economia():
    user = _user_com_baseline("fut", -18, custo_mensal=300)  # Data Zero 18 dias à frente
    assert streak_consecutivo(user, "alcool") == 0
    assert dinheiro_economizado(user) == 0
    assert dias_ate_dia1(user) == 18


@pytest.mark.django_db
def test_substituicoes_eficacia():
    from apps.baseline.models import Substitution
    from apps.log.models import CravingEvent

    user = _user_com_baseline("sub", 30)
    s = Substitution.objects.create(user=user, nome="Caminhada", categoria="movimento")
    CravingEvent.objects.create(
        user=user, timestamp=timezone.now(), substancia="tabaco",
        intensidade_pico=8, gatilho_texto="tédio", substituicao_usada=s,
        tempo_para_baixar_3=20,
    )
    CravingEvent.objects.create(
        user=user, timestamp=timezone.now(), substancia="tabaco",
        intensidade_pico=6, gatilho_texto="tédio", substituicao_usada=s,
    )
    r = substituicoes_eficacia(user)
    assert r[0]["substituicao"] == "Caminhada"
    assert r[0]["usos"] == 2
    assert r[0]["taxa_resolucao"] == 0.5
    assert r[0]["tempo_medio_min"] == 20.0
