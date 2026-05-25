from rest_framework import serializers

from .models import BacklogItem, Compra, Consulta, Decision


class BacklogItemSerializer(serializers.ModelSerializer):
    blocks = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = BacklogItem
        exclude = ["user"]


class DecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Decision
        exclude = ["user"]


class ConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consulta
        exclude = ["user"]


class CompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compra
        exclude = ["user"]
