"""Endpoints read-only que agregam apps/log/services.py (não paginados; um objeto por GET)."""

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .metrics import DashboardSerializer


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=DashboardSerializer)
    def get(self, request):
        user = request.user
        data = {
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
            "estados_frequencia": services.estados_frequencia(user),
            "triggers_frequencia": services.triggers_frequencia(user),
            "substituicoes_eficacia": services.substituicoes_eficacia(user),
        }
        return Response(data)
