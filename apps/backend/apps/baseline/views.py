from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common import OwnedModelViewSet

from . import taxonomia
from .models import BaselineProfile, EstadoInterno, IfThenPlan, Substitution, Trigger, Value
from .serializers import (
    BaselineProfileSerializer,
    EstadoInternoSerializer,
    IfThenPlanSerializer,
    SubstitutionSerializer,
    TaxonomiaEstadosSerializer,
    TaxonomiaGatilhosSerializer,
    TriggerSerializer,
    ValueSerializer,
)


class EstadoInternoViewSet(OwnedModelViewSet):
    queryset = EstadoInterno.objects.all()
    serializer_class = EstadoInternoSerializer
    filterset_fields = ["ativo"]
    search_fields = ["nome"]
    ordering_fields = ["ordem", "nome"]


class BaselineProfileViewSet(OwnedModelViewSet):
    queryset = BaselineProfile.objects.all()
    serializer_class = BaselineProfileSerializer


class ValueViewSet(OwnedModelViewSet):
    queryset = Value.objects.all()
    serializer_class = ValueSerializer
    ordering_fields = ["ordem"]


class TriggerViewSet(OwnedModelViewSet):
    queryset = Trigger.objects.all()
    serializer_class = TriggerSerializer
    filterset_fields = ["ativo", "estado_mais_comum"]
    search_fields = ["nome", "contexto"]


class SubstitutionViewSet(OwnedModelViewSet):
    queryset = Substitution.objects.all()
    serializer_class = SubstitutionSerializer
    filterset_fields = ["categoria", "ativo"]
    search_fields = ["nome"]


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
