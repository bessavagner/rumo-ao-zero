from django.db import migrations

from ._0008_helpers import migrar_estados, migrar_gatilhos


def noop(apps, schema_editor):
    """Reversível de propósito: os campos velhos ainda estão vivos nesta etapa, então desfazer é
    só não usar os novos. A 0009 é que é o ponto sem volta."""


class Migration(migrations.Migration):
    dependencies = [("log", "0007_gatilho_taxonomia_add")]

    operations = [
        migrations.RunPython(migrar_gatilhos, noop),
        migrations.RunPython(migrar_estados, noop),
    ]
