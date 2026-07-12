"""Lógica da data migration 0005 (IfThenPlan) — mesmo mapa, mesmo princípio da 0008 do log."""

from apps.baseline.taxonomia import carregar_mapa, normalizar


def migrar_ifthen(apps, schema_editor):
    mapa = carregar_mapa("gatilhos")
    IfThenPlan = apps.get_model("baseline", "IfThenPlan")
    for plano in IfThenPlan.objects.all():
        texto = plano.gatilho_texto or ""
        plano.gatilho = mapa.get(normalizar(texto), "outro")
        if texto and not plano.detalhes:
            plano.detalhes = texto
        plano.save(update_fields=["gatilho", "detalhes"])
