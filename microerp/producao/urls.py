# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# urls da Producao
urlpatterns = patterns('',
    url(r'^$', 'producao.views.home', name='home'),
    url(r'^notafiscal/lancar_nota$', 'producao.views.lancar_nota', name='lancar_nota'),
    url(r'^notafiscal/(?P<notafiscal_id>[0-9]+)/editar$', 'producao.views.editar_nota', name='editar_nota'),    
    url(r'^notafiscal/adicionar$', 'producao.views.adicionar_nota', name='adicionar_nota'),
)
