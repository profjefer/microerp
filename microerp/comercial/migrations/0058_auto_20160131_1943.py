# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-31 21:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0057_auto_20160131_1938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grupodadosvariaveis',
            name='contrato',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, to='comercial.ContratoFechado'),
        ),
        migrations.AlterField(
            model_name='grupodadosvariaveis',
            name='proposta',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, to='comercial.PropostaComercial'),
        ),
    ]