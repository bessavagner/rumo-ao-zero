from django.contrib import admin

from .models import BaselineProfile, IfThenPlan, Value


@admin.register(BaselineProfile)
class BaselineProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "data_zero", "custo_mensal_estimado", "updated_at")


@admin.register(Value)
class ValueAdmin(admin.ModelAdmin):
    list_display = ("user", "ordem", "nome")
    list_filter = ("user",)


@admin.register(IfThenPlan)
class IfThenPlanAdmin(admin.ModelAdmin):
    list_display = ("gatilho", "acao", "user", "ativo", "vezes_acionado")
    list_filter = ("user", "ativo", "gatilho")
