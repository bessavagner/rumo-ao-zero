"""Serializers de saída das métricas derivadas (documentação OpenAPI; dados vêm de services.py)."""

from rest_framework import serializers


class StreakSerializer(serializers.Serializer):
    consecutivo = serializers.IntegerField()
    ano = serializers.IntegerField()


class StreaksSerializer(serializers.Serializer):
    alcool = StreakSerializer()
    tabaco = StreakSerializer()


class DashboardSerializer(serializers.Serializer):
    dias_ate_dia1 = serializers.IntegerField()
    streaks = StreaksSerializer()
    dinheiro_economizado = serializers.FloatField()
    estados_frequencia = serializers.ListField(child=serializers.DictField())
    triggers_frequencia = serializers.ListField(child=serializers.DictField())
    substituicoes_eficacia = serializers.ListField(child=serializers.DictField())


class HumorPontoSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=["pulso", "daily"])
    timestamp = serializers.CharField()
    humor = serializers.IntegerField()
    energia = serializers.IntegerField()
    craving = serializers.IntegerField()


class HumorSeriesSerializer(serializers.Serializer):
    dias = serializers.IntegerField()
    pontos = HumorPontoSerializer(many=True)
