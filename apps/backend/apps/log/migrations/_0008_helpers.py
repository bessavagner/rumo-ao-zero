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
    """Diferente de `migrar_gatilhos`: aqui não existe `detalhes` em `DailyEntry`/`Pulso` para
    guardar o texto original. Se um nome de estado não estiver em `mapas/estados.csv`, ele NÃO
    pode virar silenciosamente "outro" — o texto do usuário sumiria para sempre assim que as
    migrations 0009 (log) + 0006 (baseline) apagarem `EstadoInterno` logo em seguida. Por isso
    a migração aborta e exige revisão humana do CSV antes de rodar de novo.
    """
    mapa = carregar_mapa("estados")
    for label in ("log.CravingEvent", "log.DailyEntry", "log.Pulso"):
        app_label, nome = label.split(".")
        Model = apps.get_model(app_label, nome)
        for registro in Model.objects.all():
            codigos = []
            for estado in registro.estados_m2m.all():
                chave = normalizar(estado.nome)
                if chave not in mapa:
                    raise RuntimeError(
                        f"estado '{estado.nome}' não está em mapas/estados.csv. "
                        "Rode `mapear_gatilhos --alvo estados --banco <db pré-migração>`, "
                        "revise, atualize o CSV e commite antes de migrar."
                    )
                codigo = mapa[chave]
                if codigo not in codigos:  # cansaço + cansado -> um código só
                    codigos.append(codigo)
            if codigos:
                registro.estados = codigos
                registro.save(update_fields=["estados"])
