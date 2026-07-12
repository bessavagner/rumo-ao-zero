# Gerada manualmente a partir de duas passagens de `makemigrations` (para evitar que o
# autodetector colapsasse o rename de `estados` (M2M) em RemoveField + AddField — ver
# task-3-report.md). Etapa 1/3 da migração do gatilho/estados para taxonomia fixa: os campos
# velhos (`gatilho_texto`, `trigger`, `estados_m2m`) continuam vivos; nada é destruído aqui.

import apps.baseline.taxonomia
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0006_alter_dailyentry_energia_alter_dailyentry_humor_and_more'),
    ]

    operations = [
        # 1) Preserva a tabela M2M e os dados: só o nome muda.
        migrations.RenameField(
            model_name='cravingevent',
            old_name='estados',
            new_name='estados_m2m',
        ),
        migrations.RenameField(
            model_name='dailyentry',
            old_name='estados',
            new_name='estados_m2m',
        ),
        migrations.RenameField(
            model_name='pulso',
            old_name='estados',
            new_name='estados_m2m',
        ),
        # 2) Campos novos — o nome final `estados` já nasce livre por causa do rename acima.
        migrations.AddField(
            model_name='cravingevent',
            name='detalhes',
            field=models.TextField(blank=True, help_text='O texto livre — opcional.'),
        ),
        migrations.AddField(
            model_name='cravingevent',
            name='gatilho',
            field=models.CharField(choices=[('frustracao_trabalho', 'Frustração no trabalho'), ('ansiedade_estresse', 'Ansiedade / estresse'), ('tedio_vazio', 'Tédio / vazio'), ('tristeza_solidao', 'Tristeza / solidão'), ('fim_expediente', 'Fim de expediente'), ('bebendo', 'Bebendo (gatilho cruzado)'), ('apos_refeicao', 'Após refeição'), ('cafe_pausa', 'Café / pausa'), ('cansaco_noite_mal_dormida', 'Cansaço / noite mal dormida'), ('dor_mal_estar', 'Dor / mal-estar'), ('comemoracao', 'Comemoração / boa notícia'), ('relaxar_recompensa', 'Relaxar, me recompensar'), ('discussao_atrito', 'Discussão / atrito'), ('evento_social', 'Evento social (bar, churrasco)'), ('alguem_ofereceu', 'Alguém me ofereceu'), ('bom_momento_proximos', 'Bom momento com gente próxima'), ('testar_um_so', 'Testar se consigo parar em um'), ('outro', 'Outro')], default='outro', max_length=32),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cravingevent',
            name='gatilhos_adicionais',
            field=models.JSONField(blank=True, default=list, validators=[apps.baseline.taxonomia.valida_situacoes]),
        ),
        migrations.AddField(
            model_name='cravingevent',
            name='estados',
            field=models.JSONField(blank=True, default=list, validators=[apps.baseline.taxonomia.valida_estados]),
        ),
        migrations.AddField(
            model_name='dailyentry',
            name='estados',
            field=models.JSONField(blank=True, default=list, validators=[apps.baseline.taxonomia.valida_estados]),
        ),
        migrations.AddField(
            model_name='pulso',
            name='estados',
            field=models.JSONField(blank=True, default=list, validators=[apps.baseline.taxonomia.valida_estados]),
        ),
        migrations.AddField(
            model_name='slip',
            name='detalhes',
            field=models.TextField(blank=True, help_text='O texto livre — opcional.'),
        ),
        migrations.AddField(
            model_name='slip',
            name='estados',
            field=models.JSONField(blank=True, default=list, validators=[apps.baseline.taxonomia.valida_estados]),
        ),
        migrations.AddField(
            model_name='slip',
            name='gatilho',
            field=models.CharField(choices=[('frustracao_trabalho', 'Frustração no trabalho'), ('ansiedade_estresse', 'Ansiedade / estresse'), ('tedio_vazio', 'Tédio / vazio'), ('tristeza_solidao', 'Tristeza / solidão'), ('fim_expediente', 'Fim de expediente'), ('bebendo', 'Bebendo (gatilho cruzado)'), ('apos_refeicao', 'Após refeição'), ('cafe_pausa', 'Café / pausa'), ('cansaco_noite_mal_dormida', 'Cansaço / noite mal dormida'), ('dor_mal_estar', 'Dor / mal-estar'), ('comemoracao', 'Comemoração / boa notícia'), ('relaxar_recompensa', 'Relaxar, me recompensar'), ('discussao_atrito', 'Discussão / atrito'), ('evento_social', 'Evento social (bar, churrasco)'), ('alguem_ofereceu', 'Alguém me ofereceu'), ('bom_momento_proximos', 'Bom momento com gente próxima'), ('testar_um_so', 'Testar se consigo parar em um'), ('outro', 'Outro')], default='outro', max_length=32),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='slip',
            name='gatilhos_adicionais',
            field=models.JSONField(blank=True, default=list, validators=[apps.baseline.taxonomia.valida_situacoes]),
        ),
        # 3) `gatilho_texto` fica sem `blank=False`->`blank=True`: o legado passa a ser opcional
        #    (o novo `gatilho` obrigatório assume o papel), mas a coluna e os dados continuam.
        migrations.AlterField(
            model_name='cravingevent',
            name='gatilho_texto',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
