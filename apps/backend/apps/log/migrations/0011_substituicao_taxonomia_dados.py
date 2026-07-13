from django.db import migrations

from ._0011_helpers import migrar_substituicoes


def noop(apps, schema_editor):
    """Reversível de propósito: nesta etapa o FK antigo ainda está vivo, então desfazer é só não
    usar os campos novos. A 0012 é que é o ponto sem volta."""


class Migration(migrations.Migration):
    dependencies = [("log", "0010_substituicao_taxonomia_add")]

    operations = [migrations.RunPython(migrar_substituicoes, noop)]
