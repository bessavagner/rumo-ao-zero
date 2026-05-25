from apps.common import OwnedModelViewSet

from .models import BacklogItem, Compra, Consulta, Decision
from .serializers import (
    BacklogItemSerializer,
    CompraSerializer,
    ConsultaSerializer,
    DecisionSerializer,
)


class BacklogItemViewSet(OwnedModelViewSet):
    queryset = BacklogItem.objects.all()
    serializer_class = BacklogItemSerializer
    filterset_fields = ["secao", "prioridade", "status", "responsavel"]
    search_fields = ["id_externo", "titulo", "contexto"]
    ordering_fields = ["id_externo", "prazo_alvo", "prioridade", "updated_at"]


class DecisionViewSet(OwnedModelViewSet):
    queryset = Decision.objects.all()
    serializer_class = DecisionSerializer
    filterset_fields = ["status", "reversibilidade"]
    search_fields = ["id_externo", "titulo"]
    ordering_fields = ["data"]


class ConsultaViewSet(OwnedModelViewSet):
    queryset = Consulta.objects.all()
    serializer_class = ConsultaSerializer
    filterset_fields = ["especialidade", "modalidade"]
    ordering_fields = ["data"]


class CompraViewSet(OwnedModelViewSet):
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer
    filterset_fields = ["categoria", "status"]
    search_fields = ["item", "fornecedor"]
    ordering_fields = ["created_at", "preco_brl"]
