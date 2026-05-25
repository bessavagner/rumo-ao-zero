from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.baseline.models import BaselineProfile
from apps.log.models import Slip
from apps.log.services import (
    dinheiro_economizado,
    streak_consecutivo,
    streak_cumulativo_ano,
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
