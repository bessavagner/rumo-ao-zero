from rest_framework import serializers

from .models import CravingEvent, DailyEntry, Pulso, Slip

# Campos que saem do payload da API. `gatilho_texto` e `trigger` ainda existem no banco (só somem
# na migration destrutiva), mas NÃO podem ser escritos nem lidos: a taxonomia é fixa e não existe
# caminho de código que crie um gatilho. `estados_m2m` é o M2M legado, idem.
LEGADO = ["user", "gatilho_texto", "trigger", "estados_m2m"]


class DailyEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyEntry
        exclude = ["user", "estados_m2m"]


class CravingEventSerializer(serializers.ModelSerializer):
    categoria = serializers.CharField(read_only=True)

    class Meta:
        model = CravingEvent
        exclude = LEGADO


class SlipSerializer(serializers.ModelSerializer):
    categoria = serializers.CharField(read_only=True)

    class Meta:
        model = Slip
        exclude = ["user", "gatilho_texto", "trigger"]


class PulsoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pulso
        exclude = ["user", "estados_m2m"]
