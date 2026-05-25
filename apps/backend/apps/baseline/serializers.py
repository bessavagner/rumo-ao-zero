from rest_framework import serializers

from .models import BaselineProfile, EstadoInterno, IfThenPlan, Substitution, Trigger, Value


class EstadoInternoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoInterno
        exclude = ["user"]


class BaselineProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaselineProfile
        exclude = ["user"]


class ValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Value
        exclude = ["user"]


class TriggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trigger
        exclude = ["user"]


class SubstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Substitution
        exclude = ["user"]


class IfThenPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = IfThenPlan
        exclude = ["user"]
