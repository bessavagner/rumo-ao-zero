from datetime import date

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.log.models import DailyEntry, Pulso

User = get_user_model()


@pytest.mark.django_db
def test_create_daily_entry_define_user_do_token():
    from apps.baseline.models import EstadoInterno

    user = User.objects.create_user(username="api", password="x")
    raiva = EstadoInterno.objects.create(user=user, nome="raiva")
    client = APIClient()
    client.force_authenticate(user=user)

    resp = client.post(
        "/api/log/daily/",
        {
            "data": str(date.today()),
            "humor": 3,
            "energia": 4,
            "sono_h": "7.0",
            "sono_q": 4,
            "craving_pico": 2,
            "estados": [raiva.id],
        },
        format="json",
    )

    assert resp.status_code == 201, resp.content
    entry = DailyEntry.objects.get()
    assert entry.user == user
    assert list(entry.estados.values_list("nome", flat=True)) == ["raiva"]


@pytest.mark.django_db
def test_endpoints_exigem_autenticacao():
    client = APIClient()
    resp = client.get("/api/log/daily/")
    assert resp.status_code in (401, 403)


@pytest.mark.django_db
def test_pulso_aceita_varios_no_mesmo_dia_e_escopa_user():
    from apps.baseline.models import EstadoInterno

    user = User.objects.create_user(username="api", password="x")
    tedio = EstadoInterno.objects.create(user=user, nome="tédio")
    client = APIClient()
    client.force_authenticate(user=user)

    # Dois pulsos no MESMO dia (intra-dia) — diferente do DailyEntry, não tem unique por data.
    primeiro = client.post(
        "/api/log/pulsos/",
        {"timestamp": "2026-06-22T10:00", "humor": 4, "energia": 4},
        format="json",
    )
    segundo = client.post(
        "/api/log/pulsos/",
        {"timestamp": "2026-06-22T16:00", "humor": 2, "energia": 2, "craving": 7, "estados": [tedio.id], "nota": "fossa"},
        format="json",
    )

    assert primeiro.status_code == 201, primeiro.content
    assert segundo.status_code == 201, segundo.content
    assert Pulso.objects.filter(user=user).count() == 2
    p = Pulso.objects.get(humor=2)
    assert p.user == user
    assert p.craving == 7
    assert p.estados.count() == 1
    assert list(p.estados.values_list("nome", flat=True)) == ["tédio"]
    # pulso sem craving usa o default 0
    assert Pulso.objects.get(humor=4).craving == 0


@pytest.mark.django_db
def test_pulso_exige_autenticacao():
    client = APIClient()
    resp = client.get("/api/log/pulsos/")
    assert resp.status_code in (401, 403)


@pytest.mark.django_db
def test_craving_autolink_cria_trigger_a_partir_do_texto():
    """Craving criado pelo SPA (só gatilho_texto) ganha um Trigger do mapa (get-or-create)."""
    from apps.baseline.models import Trigger
    from apps.log.models import CravingEvent

    user = User.objects.create_user(username="api", password="x")
    client = APIClient()
    client.force_authenticate(user=user)

    resp = client.post(
        "/api/log/cravings/",
        {"timestamp": "2026-06-22T18:00", "substancia": "alcool",
         "intensidade_pico": 7, "gatilho_texto": "fim de expediente"},
        format="json",
    )

    assert resp.status_code == 201, resp.content
    craving = CravingEvent.objects.get()
    assert craving.trigger is not None
    assert craving.trigger.nome == "fim de expediente"
    assert Trigger.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_craving_autolink_reusa_trigger_existente_case_insensitive():
    """Não duplica o Trigger: reusa o do mapa por nome (case-insensitive)."""
    from apps.baseline.models import Trigger

    user = User.objects.create_user(username="api", password="x")
    existente = Trigger.objects.create(user=user, nome="Fim de Expediente")
    client = APIClient()
    client.force_authenticate(user=user)

    resp = client.post(
        "/api/log/cravings/",
        {"timestamp": "2026-06-22T18:00", "substancia": "alcool",
         "intensidade_pico": 7, "gatilho_texto": "fim de expediente"},
        format="json",
    )

    assert resp.status_code == 201, resp.content
    assert resp.json()["trigger"] == existente.id
    assert Trigger.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_craving_editar_gatilho_texto_religa_trigger():
    from apps.baseline.models import Trigger
    from apps.log.models import CravingEvent

    user = User.objects.create_user(username="api", password="x")
    client = APIClient()
    client.force_authenticate(user=user)
    cid = client.post(
        "/api/log/cravings/",
        {"timestamp": "2026-06-22T18:00", "substancia": "alcool",
         "intensidade_pico": 7, "gatilho_texto": "tédio"},
        format="json",
    ).json()["id"]

    resp = client.patch(f"/api/log/cravings/{cid}/", {"gatilho_texto": "ansiedade"}, format="json")

    assert resp.status_code == 200, resp.content
    assert CravingEvent.objects.get(id=cid).trigger.nome == "ansiedade"
    assert set(Trigger.objects.filter(user=user).values_list("nome", flat=True)) == {"tédio", "ansiedade"}


@pytest.mark.django_db
def test_escalas_rejeitam_fora_da_faixa():
    user = User.objects.create_user(username="api", password="x")
    client = APIClient()
    client.force_authenticate(user=user)

    # humor é 1–5: 9 (acima do máx) e 0 (abaixo do mín) devem dar 400.
    acima = client.post(
        "/api/log/pulsos/",
        {"timestamp": "2026-06-22T16:00", "humor": 9, "energia": 3},
        format="json",
    )
    abaixo = client.post(
        "/api/log/pulsos/",
        {"timestamp": "2026-06-22T16:00", "humor": 0, "energia": 3},
        format="json",
    )
    # craving é 0–10: 50 deve dar 400.
    craving_alto = client.post(
        "/api/log/pulsos/",
        {"timestamp": "2026-06-22T16:00", "humor": 3, "energia": 3, "craving": 50},
        format="json",
    )

    assert acima.status_code == 400, acima.content
    assert abaixo.status_code == 400, abaixo.content
    assert craving_alto.status_code == 400, craving_alto.content
    assert Pulso.objects.count() == 0
