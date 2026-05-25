from datetime import date

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.log.models import DailyEntry

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
