# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context
from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import user_passes_test, login_required

from django import forms
from django.db.models import Q
from django.core.files.base import ContentFile
from StringIO import StringIO

# import numpy as np
# import matplotlib.pyplot as plt

from django.contrib import messages

from comercial.models import PropostaComercial, ItemGrupoDocumento

from models import TabelaValores, PorteFinanciamento

class FormConfiguraRetscreen(forms.Form):
    fator = forms.DecimalField(label=u"Fator Energético", required=True, initial=0,  decimal_places=2)
    media = forms.DecimalField(label=u"Média de Consumo Energético", required=True)
    tamanho_placa = forms.DecimalField(label=u"Tamanho da Placa", required=True, initial=0.265)
    radiacao = forms.DecimalField(label=u"Radiação", required=True, initial=4.81)
    preco_eletricidade = forms.DecimalField(label=u"Preço da Eletricidade", initial=0.50974, required=True)
    quantidade_placa = forms.DecimalField(label=u"Quantidade de Placas", required=False)
    valor_final = forms.DecimalField(label=u"Valor Final", required=False)

@login_required
def home(request):
    form = FormConfiguraRetscreen(request.POST or None)
    proposta_id = request.GET.get('proposta', request.POST.get('proposta', None))
    propostas_da_empresa = PropostaComercial.objects.filter(
        Q(precliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa) | \
        Q(cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa)
    )
    propostas_possiveis = propostas_da_empresa.filter(
        #documento_gerado__grupodocumento__itemgrupodocumento__chave_identificadora='retscreen',
        status='aberta'
    )
    if proposta_id:
        proposta = get_object_or_404(propostas_da_empresa, pk=proposta_id)
    if request.POST and form.is_valid():
        reajuste_custo_energia = float(0.08)
        messages.success(request, u"Sucesso!Form Válido")
        media = float(form.cleaned_data['media'])
        tamanho_placa = float(form.cleaned_data['tamanho_placa'])
        radiacao = float(form.cleaned_data['radiacao'])
        preco_eletricidade = float(form.cleaned_data['preco_eletricidade'])
        media_diaria = media / 30.00
        percentual_perda = (radiacao * 3) / 100
        perda = radiacao * percentual_perda
        radiacao_real = radiacao - perda
        tamanho_usina = (media_diaria / radiacao_real)
        if not form.cleaned_data['quantidade_placa']:
            numero_placas_sugerida = tamanho_usina / tamanho_placa
        else:
            numero_placas_sugerida = form.cleaned_data['quantidade_placa']
        # recacula tamanho da usina com quantidade de placas definida
        tamanho_usina = float(tamanho_placa) * float(numero_placas_sugerida)
        area_usina = float(numero_placas_sugerida) * 1.68
        geracao_kw_mes = tamanho_usina * 30 * radiacao_real
        geracao_kw_ano = geracao_kw_mes * 12
        economia_mensal = geracao_kw_mes * preco_eletricidade
        economia_anual = economia_mensal * 12
        tabela = TabelaValores.objects.get(
            quantidade_placas_inicial__lte=numero_placas_sugerida,
            quantidade_placas_final__gte=numero_placas_sugerida,
            )
        preco_por_watt = tabela.valor
        preco_sugerido = round(float(tamanho_usina) * float(preco_por_watt))
        retorno = {}
        if form.cleaned_data['valor_final']:
            preco_sugerido = float(form.cleaned_data['valor_final'])
        # calcula preco sugerido com fator
        if form.cleaned_data['fator'] != 0:
            preco_sugerido = preco_sugerido + (float(preco_sugerido) * float(form.cleaned_data['fator'])/100)

        retorno_exato = None
        for i in range(1,26):
            # primeiro registro: preço sugerido e economia anual
            retorno[i] = [round(preco_sugerido * -1, 2), round(economia_anual, 2)]
            if i != 1:
                # quanto falta pagar
                saldo_remascente = retorno[i-1][0]
                # reajuste no ano anterior
                economia_no_ano_anterior = retorno[i-1][1]
                # calcula retorno exato, em meses:
                economia_neste_ano = (economia_no_ano_anterior * reajuste_custo_energia) + economia_no_ano_anterior
                if not retorno_exato and saldo_remascente > 0:
                    retorno_exato = i-2
                    ano_retorno = retorno_exato
                    meses = saldo_remascente / (economia_neste_ano / 12)
                    retorno_exato_str = '%d Anos, %d Meses' % (ano_retorno, meses)
                retorno[i] = [
                    round(saldo_remascente + economia_neste_ano, 2),
                    economia_neste_ano
                ]
        updated_data = request.POST.copy()
        updated_data.update(
            {
                'quantidade_placa': numero_placas_sugerida,
                'valor_final': preco_sugerido
            }
        )
        form = FormConfiguraRetscreen(data=updated_data)
        # busca valores de financiamento
        financiamentos_porte = PorteFinanciamento.objects.filter(
            valor_inicial__lte=preco_sugerido,
            valor_final__gte=preco_sugerido,
        )
        if request.POST.get('inserir'):
            proposta = PropostaComercial.objects.get(pk=request.POST.get('proposta_inserir'))
            # inserir valores nos dados variaveis
            valores = []
            # formata para exibicao
            import locale
            locale.setlocale(locale.LC_ALL,"pt_BR.UTF-8")
            preco_por_watt_str = locale.currency(preco_por_watt, grouping=True)
            economia_mensal_str = locale.currency(economia_mensal, grouping=True)
            economia_anual_str = locale.currency(economia_anual, grouping=True)
            preco_sugerido_str = locale.currency(preco_sugerido, grouping=True)
            preco_eletricidade_str = locale.currency(preco_eletricidade, grouping=True)
            # registra chave, valor, tipo
            valores = \
            [
            ['seltec_preco_sugerido', preco_sugerido_str, 'texto'],
            ['seltec_tamanho_usina', round(tamanho_usina, 2), 'decimal'],
            ['seltec_quantidade_placa', round(numero_placas_sugerida, 2), 'numero'],
            ['seltec_tamanho_usina_m2', round(area_usina, 2), 'decimal'],
            ['seltec_preco_eletricidade', preco_eletricidade_str, 'texto'],
            ['seltec_reajuste_energia', reajuste_custo_energia, 'decimal'],
            ['seltec_geracao_kw_mes', geracao_kw_mes, 'decimal'],
            ['seltec_geracao_kw_ano', geracao_kw_ano, 'decimal'],
            ['seltec_economia_mensal', economia_mensal_str, 'texto'],
            ['seltec_economia_anual', economia_anual_str, 'texto'],
            ['seltec_retorno_investimento', retorno_exato_str, 'texto'],
            ]
            # insere dados variaveis
            for item in valores:
                d,c = proposta.documento_gerado.grupodadosvariaveis.dadovariavel_set.get_or_create(
                    chave=item[0],
                )
                d.valor = item[1]
                d.tipo = item[2]
                d.save()
            # salva valor de proposta
            try:
                proposta.valor_proposto = preco_sugerido
                proposta.save()
                messages.success(request, u"Valor da Proposta #%s alterado para %s" % (proposta.pk, preco_sugerido))
            except:
                raise
                messages.error(request, u"Erro! Valor da proposta não alterado")

            # pega item de referencia do retscreen
            # quantidade = ItemGrupoDocumento.objects.filter(chave_identificadora__startswith='retscreen_', grupo__documento__propostacomercial=proposta).count()
            # quantidade = quantidade + 1
            # ultimo = ItemGrupoDocumento.objects.filter(chave_identificadora='retscreen', grupo__documento__propostacomercial=proposta).last()
            # novo_item = ultimo
            # novo_item.id = None
            # novo_item.apagavel = True
            # novo_item.imagem_editavel = True
            # novo_item.chave_identificadora = 'retscreen_%s' % quantidade
            # # gera imagem
            #
            # anos = [k for k,v in retorno.items()]
            # valores = [v[0] for k,v in retorno.items()]
            # y = [3, 10, 7, 5, 3, 4.5, 6, 8.1]
            # N = len(y)
            # x = range(N)
            # width = 1/1.5
            # plt.bar(x, y, width, color="blue")
            # # fim do example
            # f = StringIO()
            # plt.savefig(f)
            # content_file = ContentFile(f.getvalue())
            # novo_item.imagem.save('teste.png', content_file)
            # novo_item.save()
            messages.info(request, 'simulação inserida na proposta %s' % proposta)
            #  redireciona pra tela de editar proposta
            return redirect(reverse("comercial:editar_proposta", args=[proposta.pk]))

    return render_to_response('frontend/retscreen/retscreen-home.html', locals(), context_instance=RequestContext(request),)
