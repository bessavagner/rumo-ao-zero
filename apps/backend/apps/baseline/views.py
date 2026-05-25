from apps.common import OwnedModelViewSet

from .models import BaselineProfile, EstadoInterno, IfThenPlan, Substitution, Trigger, Value
from .serializers import (
    BaselineProfileSerializer,
    EstadoInternoSerializer,
    IfThenPlanSerializer,
    SubstitutionSerializer,
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
