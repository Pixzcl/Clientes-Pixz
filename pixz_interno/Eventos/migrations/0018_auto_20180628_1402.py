# Generated by Django 2.0.5 on 2018-06-28 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Eventos', '0017_auto_20180628_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trabajadoresevento',
            name='Cargo',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET(None), related_name='TrabajadoresEvento', to='Eventos.Cargos', verbose_name='Cargo'),
        ),
    ]
