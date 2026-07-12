from apps.common import OwnedModelViewSet

from .models import CravingEvent, DailyEntry, Pulso, Slip
from .serializers import (
    CravingEventSerializer,
    DailyEntrySerializer,
    PulsoSerializer,
    SlipSerializer,
)


class DailyEntryViewSet(OwnedModelViewSet):
    queryset = DailyEntry.objects.all()
    serializer_class = DailyEntrySerializer
    filterset_fields = ["data", "publicable"]
    ordering_fields = ["data", "created_at"]


class CravingEventViewSet(OwnedModelViewSet):
    queryset = CravingEvent.objects.all()
    serializer_class = CravingEventSerializer
    filterset_fields = ["substancia", "publicable", "gatilho"]
    ordering_fields = ["timestamp", "intensidade_pico"]


class SlipViewSet(OwnedModelViewSet):
    queryset = Slip.objects.all()
    serializer_class = SlipSerializer
    filterset_fields = ["substancia", "gatilho"]
    ordering_fields = ["timestamp"]


class PulsoViewSet(OwnedModelViewSet):
    queryset = Pulso.objects.all()
    serializer_class = PulsoSerializer
    filterset_fields = ["humor", "energia", "craving"]
    ordering_fields = ["timestamp", "humor", "energia", "craving"]
