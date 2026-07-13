from rest_framework import serializers

from .models import CravingEvent, DailyEntry, Pulso, Slip


class DailyEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyEntry
        exclude = ["user"]


class CravingEventSerializer(serializers.ModelSerializer):
    categoria = serializers.CharField(read_only=True)

    class Meta:
        model = CravingEvent
        exclude = ["user"]


class SlipSerializer(serializers.ModelSerializer):
    categoria = serializers.CharField(read_only=True)

    class Meta:
        model = Slip
        exclude = ["user"]


class PulsoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pulso
        exclude = ["user"]
