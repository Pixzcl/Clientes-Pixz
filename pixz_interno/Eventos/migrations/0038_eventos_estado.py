# Generated by Django 2.0.5 on 2018-07-17 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Eventos', '0037_auto_20180717_1404'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventos',
            name='estado',
            field=models.IntegerField(default=0, verbose_name='Estado'),
        ),
    ]