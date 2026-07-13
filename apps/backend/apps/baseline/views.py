from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common import OwnedModelViewSet

from . import taxonomia
from .models import BaselineProfile, IfThenPlan, Value
from .serializers import (
    BaselineProfileSerializer,
    IfThenPlanSerializer,
    TaxonomiaEstadosSerializer,
    TaxonomiaGatilhosSerializer,
    TaxonomiaSubstituicoesSerializer,
    ValueSerializer,
)


class BaselineProfileViewSet(OwnedModelViewSet):
    queryset = BaselineProfile.objects.all()
    serializer_class = BaselineProfileSerializer


class ValueViewSet(OwnedModelViewSet):
    queryset = Value.objects.all()
    serializer_class = ValueSerializer
    ordering_fields = ["ordem"]


class IfThenPlanViewSet(OwnedModelViewSet):
    queryset = IfThenPlan.objects.all()
    serializer_class = IfThenPlanSerializer
    filterset_fields = ["ativo"]


class TaxonomiaGatilhosView(APIView):
    """As 18 situações agrupadas pelas 8 categorias clínicas. Read-only: a taxonomia mora em
    código (`apps/baseline/taxonomia.py`), não no banco — não há o que criar nem editar."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses=TaxonomiaGatilhosSerializer)
    def get(self, request):
        return Response(taxonomia.grupos_gatilhos())


class TaxonomiaEstadosView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=TaxonomiaEstadosSerializer)
    def get(self, request):
        return Response({"estados": taxonomia.lista_estados()})


class TaxonomiaSubstituicoesView(APIView):
    """As 5 categorias de enfrentamento. Read-only: moram em código, não no banco."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses=TaxonomiaSubstituicoesSerializer)
    def get(self, request):
        return Response({"substituicoes": taxonomia.lista_substituicoes()})
