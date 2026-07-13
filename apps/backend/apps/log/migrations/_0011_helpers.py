"""Lógica da data migration 0011 — em módulo separado para ser testável diretamente.

Não há mapa nem revisão humana aqui, diferente da migração de gatilhos: `Substitution` **já
carrega a categoria** (`categoria` sempre foi um campo com choices), então a classificação já
está feita e esta migração só a lê.

O `nome` do catálogo ("dog walking") vai para `substituicao_detalhes`: o texto nunca se perde.
"""


def migrar_substituicoes(apps, schema_editor):
    CravingEvent = apps.get_model("log", "CravingEvent")
    for craving in CravingEvent.objects.filter(substituicao_usada__isnull=False):
        sub = craving.substituicao_usada
        craving.substituicao = sub.categoria or ""
        if sub.nome and not craving.substituicao_detalhes:
            craving.substituicao_detalhes = sub.nome
        craving.save(update_fields=["substituicao", "substituicao_detalhes"])
