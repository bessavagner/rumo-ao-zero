from datetime import date

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.log.models import DailyEntry

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
            "halt": {"H": False, "A": True, "L": False, "T": True},
        },
        format="json",
    )

    assert resp.status_code == 201, resp.content
    entry = DailyEntry.objects.get()
    assert entry.user == user
    assert entry.halt["A"] is True


@pytest.mark.django_db
def test_endpoints_exigem_autenticacao():
    client = APIClient()
    resp = client.get("/api/log/daily/")
    assert resp.status_code in (401, 403)
