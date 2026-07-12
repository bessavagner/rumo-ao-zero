"""A migração executa uma decisão humana versionada — estes testes travam as duas garantias:
o texto original nunca some, e o que não casa vira 'outro' (não vira gatilho novo)."""

import pytest
from django.apps import apps as apps_reais
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.log.migrations import _0008_helpers as helpers

User = get_user_model()


@pytest.mark.django_db
def test_texto_que_casa_vira_situacao_e_preserva_o_original(monkeypatch):
    from apps.log.models import CravingEvent

    monkeypatch.setattr(helpers, "carregar_mapa", lambda nome: {"fim de expediente": "fim_expediente"})
    user = User.objects.create_user(username="mig", password="x")
    CravingEvent.objects.create(
        user=user, timestamp=timezone.now(), substancia="tabaco", intensidade_pico=8,
        gatilho_texto="Fim de Expediente", gatilho="",
    )

    helpers.migrar_gatilhos(apps_reais, None)

    c = CravingEvent.objects.get()
    assert c.gatilho == "fim_expediente"
    assert c.detalhes == "Fim de Expediente"  # o original continua lá, byte por byte


@pytest.mark.django_db
def test_texto_que_nao_casa_vira_outro_e_preserva_o_original(monkeypatch):
    from apps.log.models import Slip

    monkeypatch.setattr(helpers, "carregar_mapa", lambda nome: {})
    user = User.objects.create_user(username="mig", password="x")
    Slip.objects.create(
        user=user, timestamp=timezone.now(), substancia="alcool",
        gatilho_texto="uma coisa que só eu entendo", gatilho="",
    )

    helpers.migrar_gatilhos(apps_reais, None)

    s = Slip.objects.get()
    assert s.gatilho == "outro"
    assert s.detalhes == "uma coisa que só eu entendo"


@pytest.mark.django_db
def test_estados_colapsam_as_variacoes_e_deduplicam(monkeypatch):
    from apps.baseline.models import EstadoInterno
    from apps.log.models import CravingEvent

    monkeypatch.setattr(
        helpers, "carregar_mapa",
        lambda nome: {"cansaco": "cansaco", "cansado": "cansaco", "solidao": "solidao"},
    )
    user = User.objects.create_user(username="mig", password="x")
    cansaco = EstadoInterno.objects.create(user=user, nome="cansaço")
    cansado = EstadoInterno.objects.create(user=user, nome="cansado")
    solidao = EstadoInterno.objects.create(user=user, nome="solidão")
    c = CravingEvent.objects.create(
        user=user, timestamp=timezone.now(), substancia="tabaco",
        intensidade_pico=7, gatilho="tedio_vazio",
    )
    c.estados_m2m.add(cansaco, cansado, solidao)

    helpers.migrar_estados(apps_reais, None)

    # cansaço + cansado eram DUAS linhas no mapa antigo; viram UM código, sem duplicar.
    assert sorted(CravingEvent.objects.get().estados) == ["cansaco", "solidao"]


@pytest.mark.django_db
def test_migracao_e_no_op_em_banco_vazio(monkeypatch):
    monkeypatch.setattr(helpers, "carregar_mapa", lambda nome: {})
    helpers.migrar_gatilhos(apps_reais, None)
    helpers.migrar_estados(apps_reais, None)  # não levanta
