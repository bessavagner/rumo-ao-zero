from rest_framework import serializers

from .models import BaselineProfile, IfThenPlan, Substitution, Value


class BaselineProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaselineProfile
        exclude = ["user"]


class ValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Value
        exclude = ["user"]


class SubstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Substitution
        exclude = ["user"]


class IfThenPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = IfThenPlan
        exclude = ["user"]


class ItemTaxonomiaSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    rotulo = serializers.CharField()


class GrupoGatilhosSerializer(serializers.Serializer):
    categoria = serializers.CharField()
    rotulo = serializers.CharField()
    situacoes = ItemTaxonomiaSerializer(many=True)


class TaxonomiaGatilhosSerializer(serializers.Serializer):
    grupos = GrupoGatilhosSerializer(many=True)
    sem_categoria = ItemTaxonomiaSerializer(many=True)


class TaxonomiaEstadosSerializer(serializers.Serializer):
    estados = ItemTaxonomiaSerializer(many=True)


class TaxonomiaSubstituicoesSerializer(serializers.Serializer):
    substituicoes = ItemTaxonomiaSerializer(many=True)
