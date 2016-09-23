# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-23 11:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0068_documentogerado_arquivo_modelo'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoDePropostaDadoVariavel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chave', models.CharField(max_length=100)),
                ('tipo', models.CharField(blank=True, choices=[(b'texto', b'Texto'), (b'inteiro', 'N\xfamero  Inteiro'), (b'decimal', 'N\xfamero Decimal')], default=b'texto', max_length=100)),
            ],
        ),
    ]
