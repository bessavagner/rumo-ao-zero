from datetime import date

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.log.models import DailyEntry, Pulso

User = get_user_model()


@pytest.mark.django_db
def test_create_daily_entry_define_user_do_token():
    user = User.objects.create_user(username="api", password="x")
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
            "estados": ["raiva"],
        },
        format="json",
    )

    assert resp.status_code == 201, resp.content
    entry = DailyEntry.objects.get()
    assert entry.user == user
    assert entry.estados == ["raiva"]


@pytest.mark.django_db
def test_endpoints_exigem_autenticacao():
    client = APIClient()
    resp = client.get("/api/log/daily/")
    assert resp.status_code in (401, 403)


@pytest.mark.django_db
def test_pulso_aceita_varios_no_mesmo_dia_e_escopa_user():
    user = User.objects.create_user(username="api", password="x")
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
        {"timestamp": "2026-06-22T16:00", "humor": 2, "energia": 2, "craving": 7,
         "estados": ["tedio"], "nota": "fossa"},
        format="json",
    )

    assert primeiro.status_code == 201, primeiro.content
    assert segundo.status_code == 201, segundo.content
    assert Pulso.objects.filter(user=user).count() == 2
    p = Pulso.objects.get(humor=2)
    assert p.user == user
    assert p.craving == 7
    assert p.estados == ["tedio"]
    # pulso sem craving usa o default 0, e sem estados fica lista vazia
    assert Pulso.objects.get(humor=4).craving == 0
    assert Pulso.objects.get(humor=4).estados == []


@pytest.mark.django_db
def test_pulso_exige_autenticacao():
    client = APIClient()
    resp = client.get("/api/log/pulsos/")
    assert resp.status_code in (401, 403)


@pytest.mark.django_db
def test_craving_grava_gatilho_da_taxonomia_com_adicionais_e_detalhes():
    from apps.log.models import CravingEvent

    user = User.objects.create_user(username="api", password="x")
    client = APIClient()
    client.force_authenticate(user=user)

    resp = client.post(
        "/api/log/cravings/",
        {"timestamp": "2026-06-22T18:00", "substancia": "alcool", "intensidade_pico": 7,
         "gatilho": "fim_expediente",
         "gatilhos_adicionais": ["cansaco_noite_mal_dormida"],
         "detalhes": "bati de frente com o chefe e saí direto pro bar",
         "estados": ["cansaco"]},
        format="json",
    )

    assert resp.status_code == 201, resp.content
    craving = CravingEvent.objects.get()
    assert craving.gatilho == "fim_expediente"
    assert craving.categoria == "urges_tentacoes"
    assert craving.gatilhos_adicionais == ["cansaco_noite_mal_dormida"]
    assert craving.estados == ["cansaco"]
    assert "chefe" in craving.detalhes


@pytest.mark.django_db
def test_craving_rejeita_gatilho_fora_da_taxonomia():
    """O bug original: texto livre virava gatilho novo. Agora dá 400."""
    from apps.log.models import CravingEvent

    user = User.objects.create_user(username="api", password="x")
    client = APIClient()
    client.force_authenticate(user=user)

    texto_livre = client.post(
        "/api/log/cravings/",
        {"timestamp": "2026-06-22T18:00", "substancia": "alcool",
         "intensidade_pico": 7, "gatilho": "Fim do expediente"},
        format="json",
    )
    adicional_invalido = client.post(
        "/api/log/cravings/",
        {"timestamp": "2026-06-22T18:00", "substancia": "alcool", "intensidade_pico": 7,
         "gatilho": "tedio_vazio", "gatilhos_adicionais": ["inventado"]},
        format="json",
    )
    estado_invalido = client.post(
        "/api/log/cravings/",
        {"timestamp": "2026-06-22T18:00", "substancia": "alcool", "intensidade_pico": 7,
         "gatilho": "tedio_vazio", "estados": ["cansado"]},
        format="json",
    )

    assert texto_livre.status_code == 400, texto_livre.content
    assert "gatilho" in texto_livre.json()
    assert adicional_invalido.status_code == 400, adicional_invalido.content
    assert estado_invalido.status_code == 400, estado_invalido.content
    assert CravingEvent.objects.count() == 0


@pytest.mark.django_db
def test_craving_exige_gatilho():
    user = User.objects.create_user(username="api", password="x")
    client = APIClient()
    client.force_authenticate(user=user)

    resp = client.post(
        "/api/log/cravings/",
        {"timestamp": "2026-06-22T18:00", "substancia": "alcool", "intensidade_pico": 7},
        format="json",
    )

    assert resp.status_code == 400, resp.content
    assert "gatilho" in resp.json()


@pytest.mark.django_db
def test_slip_grava_gatilho_da_taxonomia():
    from apps.log.models import Slip

    user = User.objects.create_user(username="api", password="x")
    client = APIClient()
    client.force_authenticate(user=user)

    resp = client.post(
        "/api/log/slips/",
        {"timestamp": "2026-06-22T22:00", "substancia": "alcool", "gatilho": "evento_social",
         "detalhes": "churrasco na casa do meu irmão", "quantidade": "2 cervejas"},
        format="json",
    )

    assert resp.status_code == 201, resp.content
    assert Slip.objects.get().gatilho == "evento_social"


@pytest.mark.django_db
def test_api_nao_expoe_os_campos_legados():
    """Não pode existir caminho que crie um gatilho: gatilho_texto/trigger saem do payload."""
    user = User.objects.create_user(username="api", password="x")
    client = APIClient()
    client.force_authenticate(user=user)

    resp = client.post(
        "/api/log/cravings/",
        {"timestamp": "2026-06-22T18:00", "substancia": "alcool",
         "intensidade_pico": 7, "gatilho": "tedio_vazio"},
        format="json",
    )

    assert resp.status_code == 201, resp.content
    corpo = resp.json()
    assert "gatilho_texto" not in corpo
    assert "trigger" not in corpo


@pytest.mark.django_db
def test_escalas_rejeitam_fora_da_faixa():
    user = User.objects.create_user(username="api", password="x")
    client = APIClient()
    client.force_authenticate(user=user)

    # humor é 0–10: 11 (acima do máx) e -1 (abaixo do mín) devem dar 400.
    acima = client.post(
        "/api/log/pulsos/",
        {"timestamp": "2026-06-22T16:00", "humor": 11, "energia": 3},
        format="json",
    )
    abaixo = client.post(
        "/api/log/pulsos/",
        {"timestamp": "2026-06-22T16:00", "humor": -1, "energia": 3},
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
