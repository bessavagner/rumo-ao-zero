import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_gatilhos_devolve_situacoes_agrupadas_por_categoria():
    user = User.objects.create_user(username="tax", password="x")
    client = APIClient()
    client.force_authenticate(user=user)

    resp = client.get("/api/taxonomia/gatilhos/")

    assert resp.status_code == 200, resp.content
    data = resp.json()
    assert len(data["grupos"]) == 8
    primeiro = data["grupos"][0]
    assert primeiro["categoria"] == "emocoes_desagradaveis"
    assert {"codigo": "tedio_vazio", "rotulo": "Tédio / vazio"} in primeiro["situacoes"]
    assert data["sem_categoria"] == [{"codigo": "outro", "rotulo": "Outro"}]
    total = sum(len(g["situacoes"]) for g in data["grupos"]) + len(data["sem_categoria"])
    assert total == 18


@pytest.mark.django_db
def test_estados_devolve_lista_plana():
    user = User.objects.create_user(username="tax", password="x")
    client = APIClient()
    client.force_authenticate(user=user)

    resp = client.get("/api/taxonomia/estados/")

    assert resp.status_code == 200, resp.content
    assert {"codigo": "cansaco", "rotulo": "Cansaço"} in resp.json()["estados"]


@pytest.mark.django_db
def test_taxonomia_e_read_only_e_exige_autenticacao():
    anonimo = APIClient()
    assert anonimo.get("/api/taxonomia/gatilhos/").status_code in (401, 403)

    user = User.objects.create_user(username="tax", password="x")
    client = APIClient()
    client.force_authenticate(user=user)
    # Não existe caminho de criação de gatilho — nem aqui.
    assert client.post("/api/taxonomia/gatilhos/", {"codigo": "novo"}, format="json").status_code == 405


@pytest.mark.django_db
def test_rotas_do_catalogo_mutavel_nao_existem_mais():
    """Não há mais catálogo no banco: nada de CRUD de gatilho/estado."""
    user = User.objects.create_user(username="tax", password="x")
    client = APIClient()
    client.force_authenticate(user=user)

    assert client.get("/api/baseline/triggers/").status_code == 404
    assert client.get("/api/baseline/estados/").status_code == 404


@pytest.mark.django_db
def test_models_trigger_e_estadointerno_nao_existem_mais():
    from django.apps import apps as apps_reais

    nomes = {m.__name__ for m in apps_reais.get_app_config("baseline").get_models()}
    assert "Trigger" not in nomes
    assert "EstadoInterno" not in nomes
