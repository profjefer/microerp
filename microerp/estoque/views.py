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

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.graphics.barcode import code128
from reportlab.lib.units import mm, cm

from django.http import HttpResponse

import datetime
from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context

from django.conf import settings

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q

from estoque.models import Produto

from django_select2 import AutoModelSelect2MultipleField

#
# DECORADORES
#

def possui_perfil_acesso_estoque(user, login_url="/"):
    try:
        if user.perfilacessoestoque and user.funcionario.ativo():
            return True
    except:
        return False


def possui_perfil_acesso_estoque_gerente(user, login_url="/"):
    try:
        if user.perfilacessoestoque and user.funcionario.periodo_trabalhado_corrente and user.perfilacessoestoque.gerente and user.funcionario:
            return True
    except:
        return False


## FORMS

class SelecionaProdutosField(AutoModelSelect2MultipleField):
    queryset = Produto.objects
    search_fields = ['codigo', 'nome__icontains', 'descricao__icontains']

class SelecionaProdutos(forms.Form):
    produtos_adicionar = SelecionaProdutosField(label="Produtos para Adicionar:")

#
# VIEWS
#

@user_passes_test(possui_perfil_acesso_estoque, login_url='/')
def home(request):
    return render_to_response('frontend/estoque/estoque-home.html', locals(), context_instance=RequestContext(request),)


# ETIQUETAS
@user_passes_test(possui_perfil_acesso_estoque, login_url='/')
def etiquetas(request):
    
    # nome,id
    formatos = []
    for formato in settings.FORMATOS_ETIQUETA_SUPORTADOS:
        formatos.append((formato, settings.FORMATOS_ETIQUETA_SUPORTADOS[formato]['Codigo']))        
    
    if request.GET:
        produtos_adicionar = request.GET.getlist('produtos_adicionar')
        produtos_selecionados_get = request.GET.getlist('produtos_selecionados')
        produtos_selecionados = Produto.objects.filter(id__in=produtos_adicionar)

    form = SelecionaProdutos()
    return render_to_response('frontend/estoque/estoque-etiquetas.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_estoque, login_url='/')
def etiquetas_configurar(request):
    if request.GET.get('todos', None):
        todos = True
    return render_to_response('frontend/estoque/estoque-etiquetas-configurar.html', locals(), context_instance=RequestContext(request),)


def geraPagina(formato, numeros, c, pagesize, SHOW_BORDER=True, pular=0):
    w, h = pagesize
    i = 0
    for linha in range(formato['Linhas']):
        for coluna in range(formato['Colunas']):
            i += 1
            try:
                numero = numeros[linha][coluna]
            except IndexError:
                return
            x = formato['Esquerda']*cm + (formato['Horizontal']*cm * coluna)
            y = h - formato['Superior']*cm - (formato['Vertical']*cm * (linha) +1)
            import string
            string = string.uppercase * 4
            string = numero.descricao
            c.drawString(x+4*mm, y+(20*mm), string[0:21])
            c.drawString(x+24*mm, y+(15*mm), string[21:35])
            c.drawString(x+24*mm, y+(10*mm), string[35:49])
            c.drawString(x+24*mm, y+(5*mm), string[49:64])
            if SHOW_BORDER:
                c.rect(x, y, formato['Largura']*cm, formato['Altura']*cm)
        
            if len(numero.codigo) == 1:
                codigo = "000%d" % int(numero.codigo)
            else:
                codigo = numero.codigo
            barcode = code128.Code128(codigo, barWidth=0.26*mm, barHeight=13*mm, 
                                      quiet=False, humanReadable=True)
            barcode.drawOn(c, x+(1*mm)+(4*mm), y+(4*mm))

def _geraPaginaObjetos(formato, lista):
    l = []
    for linha in range(formato['Linhas']):
        c = []
        for coluna in range(formato['Colunas']):
            try:
                c.append(lista.pop())
            except:
                pass
        l.append(c)
    return l

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


@user_passes_test(possui_perfil_acesso_estoque, login_url='/')
def etiquetas_gerar(request):
    '''
    view que gera as etiquetas
    '''
    lista_produtos = request.GET.getlist('produtos_adicionar')
    show_border_q = request.GET.get('show_border', 0)
    formato_id = request.GET.get('formato', 17)
    if show_border_q == 0:
        show_border = False
    else:
        show_border = True

    try:
        pular_espacos = int(request.GET.get('pular_espacos', 0))
    except:
        pular_espacos = 0

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="etiquetas.pdf"'
    try:
        formato = settings.FORMATOS_ETIQUETA_SUPORTADOS[int(formato_id)]
    except:
        formato = settings.FORMATOS_ETIQUETA_SUPORTADOS[17]
    pagesize = formato['Papel'] == 'A4' and A4 or letter
    c = canvas.Canvas(response)
    
    if lista_produtos:
        produtos = Produto.objects.filter(id__in=lista_produtos, ativo=True)
    else:
        produtos = Produto.objects.filter(ativo=True)
    total = formato['Colunas'] * formato['Linhas']
    # ordena por grupo
    produtos.order_by('tipo')
    objetos_por_pagina = list(chunks(produtos, total))
    
    # SISTEMA DE IMPRESSAO DE AVULSOS
    try:
        pular = int(pular_espacos)
    except:
        pular = 0
    
    for pagina_objetos in objetos_por_pagina:
        
        numeros = _geraPaginaObjetos(formato, pagina_objetos)
        for item in range(1, pular_espacos+1):
            numeros.insert(0, None)
        #lista_objetos = [objeto for objeto in pagina_objetos]
        
        geraPagina(formato, numeros, c, pagesize, SHOW_BORDER=show_border, pular=pular)
        c.setPageSize(pagesize)
        c.showPage()
    c.save()
    return response
    
    
    for pagina in objetos_por_pagina:
        lista_objetos = [objeto for objeto in pagina]
        l = []
        for linha in range(formato['Linhas']):
            cols = []
            for coluna in range(formato['Colunas']):
                cols.append(lista_objetos.pop())
            l.append(cols)
        return l
    # retorna
    return response
        
from django.views.decorators.csrf import csrf_exempt    
from django.utils import simplejson

@csrf_exempt
def ajax_consulta_produto(request):
    q = request.GET.get('q', None)
    id_produto = request.GET.get('id', None)
    if q:
        produtos = Produto.objects.filter(
        Q(nome__icontains=q) |
        Q(codigo__icontains=q)
        )
    if id_produto:
        produto = Produto.objects.get(
            pk=id_produto
        )
        result={"text":"%s - %s" % (produto.codigo,produto.nome), "id": str(produto.id)}
        return HttpResponse(simplejson.dumps(result), mimetype='application/json')
    result = []
    for produto in produtos:
        result.append({"text":"%s - %s" % (produto.codigo,produto.nome), "id": str(produto.id)})
    return HttpResponse(simplejson.dumps(result), mimetype='application/json')

