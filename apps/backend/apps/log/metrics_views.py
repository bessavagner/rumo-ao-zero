"""Endpoints read-only que agregam apps/log/services.py (não paginados; um objeto por GET)."""

from datetime import datetime, time, timedelta

from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .metrics import DashboardSerializer, HumorSeriesSerializer
from .models import DailyEntry, Pulso


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=DashboardSerializer)
    def get(self, request):
        user = request.user
        try:
            dias = int(request.query_params.get("dias", 30))
        except ValueError:
            dias = 30
        data = {
            "dias": dias,
            "dias_ate_dia1": services.dias_ate_dia1(user),
            "streaks": {
                "alcool": {
                    "consecutivo": services.streak_consecutivo(user, "alcool"),
                    "ano": services.streak_cumulativo_ano(user, "alcool"),
                },
                "tabaco": {
                    "consecutivo": services.streak_consecutivo(user, "tabaco"),
                    "ano": services.streak_cumulativo_ano(user, "tabaco"),
                },
            },
            "dinheiro_economizado": round(services.dinheiro_economizado(user), 2),
            "estados_frequencia": services.estados_frequencia(user, dias),
            "triggers_frequencia": services.triggers_frequencia(user, dias),
            "substituicoes_eficacia": services.substituicoes_eficacia(user),
        }
        return Response(data)


class HumorSeriesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=HumorSeriesSerializer)
    def get(self, request):
        try:
            dias = int(request.query_params.get("dias", 30))
        except ValueError:
            dias = 30
        desde = timezone.localdate() - timedelta(days=dias)
        pontos = []
        for p in Pulso.objects.filter(user=request.user, timestamp__date__gte=desde):
            pontos.append({
                "tipo": "pulso",
                "timestamp": timezone.localtime(p.timestamp).isoformat(),
                "humor": p.humor, "energia": p.energia, "craving": p.craving,
                "_sort": timezone.localtime(p.timestamp),
            })
        for d in DailyEntry.objects.filter(user=request.user, data__gte=desde):
            pontos.append({
                "tipo": "daily",
                "timestamp": d.data.isoformat(),
                "humor": d.humor, "energia": d.energia, "craving": d.craving_pico,
                "_sort": timezone.make_aware(datetime.combine(d.data, time.min)),
            })
        pontos.sort(key=lambda x: x["_sort"])
        for x in pontos:
            del x["_sort"]
        return Response({"dias": dias, "pontos": pontos})
