from rest_framework import serializers

from apps.baseline.models import Trigger

from .models import CravingEvent, DailyEntry, Pulso, Slip


class _TriggerAutoLinkMixin:
    """Liga craving/slip a um Trigger do mapa (get-or-create por nome) a partir do
    ``gatilho_texto`` quando o cliente não manda ``trigger`` explícito.

    Mantém o mapa de gatilhos canônico independente do cliente (SPA, MCP, CLI) e faz o
    dashboard agrupar pelo Trigger (``trigger__nome``) em vez do texto solto. Match
    case-insensitive; se nenhum existir, cria. ``trigger`` explícito do cliente vence.
    """

    def _autolink_trigger(self, validated_data, user):
        if validated_data.get("trigger") is not None:
            return
        nome = (validated_data.get("gatilho_texto") or "").strip()
        if not nome:
            return
        trigger = Trigger.objects.filter(user=user, nome__iexact=nome).order_by("id").first()
        if trigger is None:
            trigger = Trigger.objects.create(user=user, nome=nome)
        validated_data["trigger"] = trigger

    def create(self, validated_data):
        self._autolink_trigger(validated_data, validated_data["user"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Num PATCH parcial, só re-liga se o gatilho_texto veio no payload.
        if "gatilho_texto" in validated_data:
            self._autolink_trigger(validated_data, instance.user)
        return super().update(instance, validated_data)


class DailyEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyEntry
        exclude = ["user"]


class CravingEventSerializer(_TriggerAutoLinkMixin, serializers.ModelSerializer):
    class Meta:
        model = CravingEvent
        exclude = ["user"]


class SlipSerializer(_TriggerAutoLinkMixin, serializers.ModelSerializer):
    class Meta:
        model = Slip
        exclude = ["user"]


class PulsoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pulso
        exclude = ["user"]
