from django.contrib import admin

from .models import BaselineProfile, IfThenPlan, Substitution, Trigger, Value


@admin.register(BaselineProfile)
class BaselineProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "data_zero", "custo_mensal_estimado", "updated_at")


@admin.register(Value)
class ValueAdmin(admin.ModelAdmin):
    list_display = ("user", "ordem", "nome")
    list_filter = ("user",)


@admin.register(Trigger)
class TriggerAdmin(admin.ModelAdmin):
    list_display = ("nome", "user", "halt_mais_comum", "frequencia_semana", "ativo")
    list_filter = ("user", "ativo", "halt_mais_comum")
    search_fields = ("nome", "contexto")


@admin.register(Substitution)
class SubstitutionAdmin(admin.ModelAdmin):
    list_display = ("nome", "user", "categoria", "eficacia_media", "vezes_usado", "ativo")
    list_filter = ("user", "categoria", "ativo")
    search_fields = ("nome",)


@admin.register(IfThenPlan)
class IfThenPlanAdmin(admin.ModelAdmin):
    list_display = ("gatilho_texto", "user", "ativo", "vezes_acionado")
    list_filter = ("user", "ativo")
