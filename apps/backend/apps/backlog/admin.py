from django.contrib import admin

from .models import BacklogItem, Compra, Consulta, Decision


@admin.register(BacklogItem)
class BacklogItemAdmin(admin.ModelAdmin):
    list_display = ("id_externo", "titulo", "secao", "prioridade", "status", "prazo_alvo")
    list_filter = ("user", "secao", "prioridade", "status", "responsavel")
    search_fields = ("id_externo", "titulo", "contexto")
    filter_horizontal = ("blocked_by",)


@admin.register(Decision)
class DecisionAdmin(admin.ModelAdmin):
    list_display = ("id_externo", "titulo", "status", "data", "reversibilidade")
    list_filter = ("user", "status", "reversibilidade")
    search_fields = ("id_externo", "titulo")
    filter_horizontal = ("relacionada_a",)


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ("data", "especialidade", "profissional", "modalidade", "custo_brl")
    list_filter = ("user", "especialidade", "modalidade")
    filter_horizontal = ("itens_impactados",)


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ("item", "categoria", "status", "preco_brl", "fornecedor")
    list_filter = ("user", "categoria", "status")
    search_fields = ("item", "fornecedor")
    filter_horizontal = ("itens_atendidos",)
