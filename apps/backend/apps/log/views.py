from apps.common import OwnedModelViewSet

from .models import CravingEvent, DailyEntry, Slip
from .serializers import CravingEventSerializer, DailyEntrySerializer, SlipSerializer


class DailyEntryViewSet(OwnedModelViewSet):
    queryset = DailyEntry.objects.all()
    serializer_class = DailyEntrySerializer
    filterset_fields = ["data", "publicable"]
    ordering_fields = ["data", "created_at"]


class CravingEventViewSet(OwnedModelViewSet):
    queryset = CravingEvent.objects.all()
    serializer_class = CravingEventSerializer
    filterset_fields = ["substancia", "publicable"]
    ordering_fields = ["timestamp", "intensidade_pico"]


class SlipViewSet(OwnedModelViewSet):
    queryset = Slip.objects.all()
    serializer_class = SlipSerializer
    filterset_fields = ["substancia"]
    ordering_fields = ["timestamp"]
