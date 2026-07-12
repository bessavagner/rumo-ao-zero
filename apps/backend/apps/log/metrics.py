"""Serializers de saída das métricas derivadas (documentação OpenAPI; dados vêm de services.py)."""

from rest_framework import serializers


class StreakSerializer(serializers.Serializer):
    consecutivo = serializers.IntegerField()
    ano = serializers.IntegerField()


class StreaksSerializer(serializers.Serializer):
    alcool = StreakSerializer()
    tabaco = StreakSerializer()


class SituacaoFreqSerializer(serializers.Serializer):
    situacao = serializers.CharField()
    rotulo = serializers.CharField()
    ocorrencias = serializers.IntegerField()


class CategoriaFreqSerializer(serializers.Serializer):
    categoria = serializers.CharField()
    rotulo = serializers.CharField()
    ocorrencias = serializers.IntegerField()


class CoocorrenciaSerializer(serializers.Serializer):
    situacao = serializers.CharField()
    rotulo = serializers.CharField()
    adicional = serializers.CharField()
    rotulo_adicional = serializers.CharField()
    ocorrencias = serializers.IntegerField()


class TriggersFrequenciaSerializer(serializers.Serializer):
    por_situacao = SituacaoFreqSerializer(many=True)
    por_categoria = CategoriaFreqSerializer(many=True)
    coocorrencia = CoocorrenciaSerializer(many=True)


class DashboardSerializer(serializers.Serializer):
    dias = serializers.IntegerField()
    dias_ate_dia1 = serializers.IntegerField()
    streaks = StreaksSerializer()
    dinheiro_economizado = serializers.FloatField()
    estados_frequencia = serializers.ListField(child=serializers.DictField())
    triggers_frequencia = TriggersFrequenciaSerializer()
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
