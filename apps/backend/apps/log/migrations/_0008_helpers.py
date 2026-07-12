"""Lógica da data migration 0008 — em módulo separado para ser testável diretamente.

Princípio inegociável: o texto original NUNCA é apagado. Ele é copiado para `detalhes` tenha
casado com uma situação ou não. Se a classificação errar, o que o usuário escreveu continua lá.
"""

from apps.baseline.taxonomia import carregar_mapa, normalizar


def _situacao(mapa: dict[str, str], texto: str) -> str:
    return mapa.get(normalizar(texto or ""), "outro")


def migrar_gatilhos(apps, schema_editor):
    mapa = carregar_mapa("gatilhos")
    for label in ("log.CravingEvent", "log.Slip"):
        app_label, nome = label.split(".")
        Model = apps.get_model(app_label, nome)
        for registro in Model.objects.all():
            texto = registro.gatilho_texto or ""
            registro.gatilho = _situacao(mapa, texto)
            if texto and not registro.detalhes:
                registro.detalhes = texto
            registro.save(update_fields=["gatilho", "detalhes"])


def migrar_estados(apps, schema_editor):
    mapa = carregar_mapa("estados")
    for label in ("log.CravingEvent", "log.DailyEntry", "log.Pulso"):
        app_label, nome = label.split(".")
        Model = apps.get_model(app_label, nome)
        for registro in Model.objects.all():
            codigos = []
            for estado in registro.estados_m2m.all():
                codigo = mapa.get(normalizar(estado.nome), "outro")
                if codigo not in codigos:  # cansaço + cansado -> um código só
                    codigos.append(codigo)
            if codigos:
                registro.estados = codigos
                registro.save(update_fields=["estados"])
