import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from apps.backlog.models import BacklogItem

User = get_user_model()


@pytest.mark.django_db
def test_id_externo_unico_por_usuario():
    user = User.objects.create_user(username="a", password="x")
    BacklogItem.objects.create(user=user, id_externo="1.1.1", titulo="X", secao="saude")
    with pytest.raises(IntegrityError):
        BacklogItem.objects.create(user=user, id_externo="1.1.1", titulo="Y", secao="saude")


@pytest.mark.django_db
def test_blocked_by_e_reverso_blocks():
    user = User.objects.create_user(username="b", password="x")
    consulta = BacklogItem.objects.create(user=user, id_externo="1.1.1", titulo="consulta", secao="saude")
    comprar = BacklogItem.objects.create(user=user, id_externo="1.1.3", titulo="comprar med", secao="saude")

    comprar.blocked_by.add(consulta)

    assert list(consulta.blocks.all()) == [comprar]
    assert list(comprar.blocked_by.all()) == [consulta]
