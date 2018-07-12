# Generated by Django 2.0.5 on 2018-07-10 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Eventos', '0028_auto_20180710_1719'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='facturas',
            name='idFacturacion',
        ),
        migrations.AlterField(
            model_name='facturas',
            name='nFactura',
            field=models.PositiveSmallIntegerField(error_messages={'unique': 'Ya existe este número de factura.'}, primary_key=True, serialize=False, unique=True, verbose_name='N° de factura'),
        ),
    ]
