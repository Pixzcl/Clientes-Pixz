# Generated by Django 2.0.5 on 2018-08-28 00:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Eventos', '0048_auto_20180827_2121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='costosvariables',
            name='documento',
            field=models.CharField(max_length=255, verbose_name='Documento'),
        ),
    ]
