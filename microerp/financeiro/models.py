# -*- coding: utf-8 -*-
"""This file is part of the microerp project.

This program is free software: you can redistribute it and/or modify it 
under the terms of the GNU Lesser General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

__author__ = 'Duda Nogueira <dudanogueira@gmail.com>'
__copyright__ = 'Copyright (c) 2013 Duda Nogueira'
__version__ = '0.0.1'

#CONTRATO_FORMA_DE_PAGAMENTO_CHOICES = (
#    ('boleto', 'Boleto'),
#    ('credito', u'Cartão de Crédito'),
#    ('debito', u'Cartão de Débito'),
#    ('dinheiro', 'Dinheiro'),
#    ('cheque', 'Cheque'),
#    ('permuta', 'Permuta'),
#)

from comercial.models import CONTRATO_FORMA_DE_PAGAMENTO_CHOICES
LANCAMENTO_MODO_RECEBIDO_CHOICES = CONTRATO_FORMA_DE_PAGAMENTO_CHOICES


LANCAMENTO_SITUACAO_CHOICES = (
    ('a','Aberto'),
    ('r','Recebido'),
    ('p','Pendente'),
)

import datetime
from django.db import models

from django.conf import settings

class PerfilAcessoFinanceiro(models.Model):
    '''Perfil de Acesso ao Financeiro'''
    
    class Meta:
        verbose_name = u"Perfil de Acesso ao Financeiro"
        verbose_name_plural = u"Perfis de Acesso ao Financeiro"
    
    gerente = models.BooleanField(default=False)
    analista = models.BooleanField(default=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")

class ContaBancaria(models.Model):
    
    def __unicode__(self):
        return self.nome
    
    nome = models.CharField(blank=True, max_length=100)

class Lancamento(models.Model):
    
    def __unicode__(self):
        if self.data_recebido:
            return u"Lançamento de peso %d RECEBIDO em %s do Contrato #%d, Cliente %s de R$%s para %s" % (self.peso, self.data_recebido, self.contrato.id, self.contrato.cliente, self.valor_cobrado, self.data_cobranca)
        else:
            return u"Lançamento de peso %d  A RECEBER do Contrato #%d, Cliente %s de R$%s para %s" % (self.peso, self.contrato.id, self.contrato.cliente, self.valor_cobrado, self.data_cobranca)
    
    
    
    def clean(self):
        if self.data_recebido and not self.modo_recebido:
            raise ValidationError(u"Erro. Para receber o valor, é preciso especificar o modo recebido")
    
    class Meta:
        unique_together = (('contrato', 'peso'),)
    
    contrato = models.ForeignKey('comercial.ContratoFechado')
    peso = models.IntegerField(blank=False, null=False, default=1)
    situacao = models.CharField(blank=False, default="a", choices=LANCAMENTO_SITUACAO_CHOICES, max_length=1)
    data_cobranca = models.DateField(default=datetime.datetime.today)
    valor_cobrado = models.DecimalField("Valor Cobrado", max_digits=10, decimal_places=2)
    valor_recebido = models.DecimalField("Valor Recebido", max_digits=10, decimal_places=2, blank=True, null=True)
    modo_recebido = models.CharField(blank=True, null=True, max_length=100, choices=LANCAMENTO_MODO_RECEBIDO_CHOICES)
    data_recebido = models.DateField(blank=True, null=True)
    data_recebido_em_conta = models.DateField(blank=True, null=True)
    conta = models.ForeignKey('ContaBancaria', blank=True, null=True)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")