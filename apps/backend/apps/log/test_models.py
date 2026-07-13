"""Validação da taxonomia no nível do model (full_clean) — a API herda estes validators."""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.baseline.models import IfThenPlan
from apps.log.models import CravingEvent, DailyEntry, Slip

User = get_user_model()


def _craving(user, **kwargs):
    campos = dict(
        user=user, timestamp=timezone.now(), substancia="tabaco",
        intensidade_pico=7, gatilho="tedio_vazio",
    )
    campos.update(kwargs)
    return CravingEvent(**campos)


@pytest.mark.django_db
def test_gatilho_fora_da_lista_e_rejeitado():
    user = User.objects.create_user(username="m", password="x")
    with pytest.raises(ValidationError) as exc:
        _craving(user, gatilho="fim de expediente").full_clean()
    assert "gatilho" in exc.value.message_dict


@pytest.mark.django_db
def test_gatilhos_adicionais_so_aceita_codigos_da_lista():
    user = User.objects.create_user(username="m", password="x")
    _craving(user, gatilhos_adicionais=["cansaco_noite_mal_dormida", "bebendo"]).full_clean()
    with pytest.raises(ValidationError) as exc:
        _craving(user, gatilhos_adicionais=["inventado"]).full_clean()
    assert "gatilhos_adicionais" in exc.value.message_dict
    with pytest.raises(ValidationError):
        _craving(user, gatilhos_adicionais="tedio_vazio").full_clean()  # string, não lista


@pytest.mark.django_db
def test_estados_so_aceita_codigos_da_lista():
    user = User.objects.create_user(username="m", password="x")
    _craving(user, estados=["cansaco", "solidao"]).full_clean()
    with pytest.raises(ValidationError) as exc:
        _craving(user, estados=["cansado"]).full_clean()  # a variação de digitação morre aqui
    assert "estados" in exc.value.message_dict

    entry = DailyEntry(
        user=user, data=timezone.localdate(), humor=5, energia=5, sono_h="7.0", sono_q=5,
        estados=["fome"],
    )
    entry.full_clean()


@pytest.mark.django_db
def test_categoria_e_property_derivada_e_none_para_outro():
    user = User.objects.create_user(username="m", password="x")
    assert _craving(user, gatilho="fim_expediente").categoria == "urges_tentacoes"
    assert _craving(user, gatilho="outro").categoria is None
    slip = Slip(user=user, timestamp=timezone.now(), substancia="alcool", gatilho="evento_social")
    assert slip.categoria == "pressao_social"
    plano = IfThenPlan(user=user, gatilho="fim_expediente", acao="caminhar 10 min")
    assert plano.categoria == "urges_tentacoes"


@pytest.mark.django_db
def test_detalhes_e_opcional_e_guarda_o_texto_livre():
    user = User.objects.create_user(username="m", password="x")

    # Vazio é válido: `detalhes` é opcional.
    vazio = _craving(user, detalhes="")
    vazio.full_clean()
    vazio.save()
    assert CravingEvent.objects.get(pk=vazio.pk).detalhes == ""

    # Com texto: o que o usuário escreveu precisa voltar intacto do banco.
    texto = "briga no trabalho, saí pra fumar (acentuação e vírgula precisam sobreviver)"
    com_texto = _craving(user, detalhes=texto)
    com_texto.full_clean()
    com_texto.save()
    assert CravingEvent.objects.get(pk=com_texto.pk).detalhes == texto


@pytest.mark.django_db
def test_substituicao_fora_das_cinco_e_rejeitada():
    user = User.objects.create_user(username="m", password="x")
    with pytest.raises(ValidationError) as exc:
        _craving(user, substituicao="corrida").full_clean()
    assert "substituicao" in exc.value.message_dict


@pytest.mark.django_db
def test_substituicao_vazia_e_valida_e_significa_nao_registrei():
    user = User.objects.create_user(username="m", password="x")
    c = _craving(user, substituicao="")
    c.full_clean()
    c.save()
    assert CravingEvent.objects.get(pk=c.pk).substituicao == ""


@pytest.mark.django_db
def test_substituicao_guarda_categoria_e_o_texto_livre():
    user = User.objects.create_user(username="m", password="x")
    c = _craving(user, substituicao="movimento", substituicao_detalhes="corri 5k no fim da tarde")
    c.full_clean()
    c.save()
    salvo = CravingEvent.objects.get(pk=c.pk)
    assert salvo.substituicao == "movimento"
    assert salvo.substituicao_detalhes == "corri 5k no fim da tarde"
