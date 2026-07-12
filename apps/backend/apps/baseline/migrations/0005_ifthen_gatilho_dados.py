from django.db import migrations

from ._0005_helpers import migrar_ifthen


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [("baseline", "0004_ifthen_gatilho_add")]

    operations = [migrations.RunPython(migrar_ifthen, noop)]
