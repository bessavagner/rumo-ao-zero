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
def test_substituicoes_eficacia_agrupa_por_categoria():
    """Regressão do bug do catálogo: 'dog walking' e 'passear com o cachorro' eram duas linhas
    dividindo a mesma estatística. Agora as duas são `movimento`, e viram UMA linha com usos=2."""
    from apps.log.models import CravingEvent

    user = _user_com_baseline("sub", 30)
    CravingEvent.objects.create(
        user=user, timestamp=timezone.now(), substancia="tabaco", intensidade_pico=8,
        gatilho="tedio_vazio", substituicao="movimento",
        substituicao_detalhes="dog walking", tempo_para_baixar_3=20,
    )
    CravingEvent.objects.create(
        user=user, timestamp=timezone.now(), substancia="tabaco", intensidade_pico=6,
        gatilho="tedio_vazio", substituicao="movimento",
        substituicao_detalhes="passear com o cachorro",
    )

    r = substituicoes_eficacia(user)

    assert len(r) == 1
    assert r[0]["substituicao"] == "movimento"
    assert "correr" in r[0]["rotulo"]
    assert r[0]["usos"] == 2
    assert r[0]["taxa_resolucao"] == 0.5   # só um dos dois baixou para ≤3
    assert r[0]["tempo_medio_min"] == 20.0


@pytest.mark.django_db
def test_craving_sem_substituicao_nao_entra_no_card():
    from apps.log.models import CravingEvent

    user = _user_com_baseline("sub2", 30)
    CravingEvent.objects.create(
        user=user, timestamp=timezone.now(), substancia="tabaco", intensidade_pico=7,
        gatilho="tedio_vazio", substituicao="",
    )

    assert substituicoes_eficacia(user) == []


@pytest.mark.django_db
def test_estados_frequencia():
    from apps.log.models import CravingEvent
    from apps.log.services import estados_frequencia

    user = _user_com_baseline("est", 30)
    CravingEvent.objects.create(
        user=user, timestamp=timezone.now(), substancia="tabaco", intensidade_pico=7,
        gatilho="tedio_vazio", estados=["cansaco", "solidao"],
    )
    CravingEvent.objects.create(
        user=user, timestamp=timezone.now(), substancia="tabaco", intensidade_pico=6,
        gatilho="cafe_pausa", estados=["cansaco"],
    )

    r = estados_frequencia(user)
    assert r[0] == {"estado": "cansaco", "rotulo": "Cansaço", "ocorrencias": 2}


@pytest.mark.django_db
def test_duas_digitacoes_do_mesmo_gatilho_viram_uma_barra_com_2():
    """Regressão do bug que originou a spec: 'fim de expediente' e 'Fim do expediente' davam
    duas barras de 1. Agora é impossível — os dois são o mesmo código."""
    from apps.log.models import CravingEvent
    from apps.log.services import triggers_frequencia

    user = _user_com_baseline("bar", 30)
    for detalhe in ("fim de expediente", "Fim do expediente"):
        CravingEvent.objects.create(
            user=user, timestamp=timezone.now(), substancia="tabaco", intensidade_pico=7,
            gatilho="fim_expediente", detalhes=detalhe,
        )

    barras = triggers_frequencia(user)["por_situacao"]
    assert barras == [
        {"situacao": "fim_expediente", "rotulo": "Fim de expediente", "ocorrencias": 2}
    ]


@pytest.mark.django_db
def test_adicionais_nao_somam_nas_barras_e_alimentam_a_coocorrencia():
    """Um craving com 3 adicionais soma 1 na barra do principal, não 4 — senão 'qual é o meu
    pior gatilho' fica errado de novo."""
    from apps.log.models import CravingEvent
    from apps.log.services import triggers_frequencia

    user = _user_com_baseline("coo", 30)
    CravingEvent.objects.create(
        user=user, timestamp=timezone.now(), substancia="tabaco", intensidade_pico=9,
        gatilho="tedio_vazio",
        gatilhos_adicionais=["cansaco_noite_mal_dormida", "bebendo", "cafe_pausa"],
    )

    r = triggers_frequencia(user)
    assert r["por_situacao"] == [
        {"situacao": "tedio_vazio", "rotulo": "Tédio / vazio", "ocorrencias": 1}
    ]
    coocorrencias = {(c["situacao"], c["adicional"]): c["ocorrencias"] for c in r["coocorrencia"]}
    assert coocorrencias == {
        ("tedio_vazio", "cansaco_noite_mal_dormida"): 1,
        ("tedio_vazio", "bebendo"): 1,
        ("tedio_vazio", "cafe_pausa"): 1,
    }


@pytest.mark.django_db
def test_por_categoria_agrega_pela_lente_do_ids_iss():
    from apps.log.models import CravingEvent
    from apps.log.services import triggers_frequencia

    user = _user_com_baseline("cat", 30)
    # Duas situações diferentes, MESMA categoria (urges e tentações) — e uma sem categoria.
    for gatilho in ("fim_expediente", "cafe_pausa", "outro"):
        CravingEvent.objects.create(
            user=user, timestamp=timezone.now(), substancia="tabaco",
            intensidade_pico=7, gatilho=gatilho,
        )

    por_categoria = triggers_frequencia(user)["por_categoria"]
    assert por_categoria == [
        {"categoria": "urges_tentacoes", "rotulo": "Urges e tentações", "ocorrencias": 2}
    ]  # 'outro' não tem categoria: não aparece nesta lente
