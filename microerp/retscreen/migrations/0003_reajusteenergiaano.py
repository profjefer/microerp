# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-06 11:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retscreen', '0002_auto_20160809_0941'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReajusteEnergiaAno',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ano', models.IntegerField(blank=True, null=True)),
                ('percentual', models.DecimalField(decimal_places=2, max_digits=5)),
                ('criado', models.DateTimeField(auto_now_add=True, verbose_name='Criado')),
                ('atualizado', models.DateTimeField(auto_now=True, verbose_name='Atualizado')),
            ],
        ),
    ]
