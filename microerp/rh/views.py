# -*- coding: utf-8 -*-
import datetime, operator
from collections import OrderedDict
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext, loader, Context
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import user_passes_test, login_required

from django.db.models import Q, Sum

from rh.models import Departamento, Funcionario, Demissao
from rh.models import FolhaDePonto, RotinaExameMedico, SolicitacaoDeLicenca
from rh.models import EntradaFolhaDePonto, Competencia
from rh.models import PeriodoTrabalhado, AtribuicaoDeCargo
from rh.models import Cargo, PromocaoCargo, PromocaoSalario, TIPO_DE_CARGO_CHOICES
from rh.models import AtribuicaoDeResponsabilidade, SubProcedimento, CapacitacaoDeSubProcedimento
from rh.models import AutorizacaoHoraExtra
from rh.utils import get_weeks
from estoque.models import Produto
from cadastro.models import EnderecoEmpresa


from django import forms
from django.conf import settings

from almoxarifado.models import ControleDeEquipamento, LinhaControleEquipamento

#
# FORMULARIOS
#
class DemitirFuncionarioForm(forms.Form):
    exame_demissional = forms.DateTimeField(
        initial=datetime.datetime.now(),
        help_text="Formato: dd/mm/yyyy HH:MM"
    )

#
class AgendarExameMedicoForm(forms.ModelForm):
    class Meta:
        model = RotinaExameMedico
        fields = ('data',)

#
class AdicionarFolhaDePontoForm(forms.ModelForm):
    class Meta:
        model = FolhaDePonto
        fields = ('data_referencia',)

#
class AdicionarEntradaFolhaDePontoForm(forms.ModelForm):
    class Meta:
        model = EntradaFolhaDePonto
        fields = ('inicio', 'fim', 'total')

#
class AdicionarArquivoRotinaExameForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AdicionarArquivoRotinaExameForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = True

    class Meta:
        model = RotinaExameMedico
        fields = ('arquivo',)

#
class AdicionarSolicitacaoLicencaForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(AdicionarSolicitacaoLicencaForm, self).__init__(*args, **kwargs)
        self.fields['inicio'].widget.attrs['class'] = 'datepicker'
        self.fields['fim'].widget.attrs['class'] = 'datepicker'
    
    class Meta:
        model = SolicitacaoDeLicenca
        fields = ('tipo', 'motivo', 'inicio', 'fim')
#
# DECORATORS
#
def possui_perfil_acesso_rh(user, login_url="/"):
    try:
        if user.perfilacessorh and user.funcionario.ativo():
            return True
    except:
        return False

#
# VIEWS
#
@user_passes_test(possui_perfil_acesso_rh)
def home(request):
    # demissoes
    demissoes_andamento = Demissao.objects.filter(status="andamento")
    # exames por vir
    semana_exibir = get_weeks()[0]
    inicio_semana = semana_exibir[0]
    fim_semana = semana_exibir[-1]
    exames_semana = RotinaExameMedico.objects.filter(data__range=(inicio_semana,fim_semana)).order_by('data')
    retorno_equipamento_semana = LinhaControleEquipamento.objects.filter(data_previsao_devolucao__range=(inicio_semana,fim_semana)).order_by('data_previsao_devolucao')
    # aniversarios
    this_week = get_weeks()[0]
    days = [day.day for day in this_week]
    today = datetime.date.today()
    aniversarios_mes = Funcionario.objects.filter(nascimento__month=today.month).exclude(periodo_trabalhado_corrente=None).extra(
        select={'birthmonth': 'MONTH(nascimento)'}, order_by=['birthmonth']
        )
    aniversarios_hoje = Funcionario.objects.filter(nascimento__month=today.month, nascimento__day=today.day)
    return render(request, 'frontend/rh/rh-home.html', locals())

#
@user_passes_test(possui_perfil_acesso_rh)
def funcionarios(request):
    funcionarios_ativos = Funcionario.objects.all().exclude(periodo_trabalhado_corrente=None).order_by('cargo_atual__departamento__nome', 'cargo_atual__nome')
    funcionarios_ativos_valores =  funcionarios_ativos.values(
        'cargo_atual__departamento__nome',
        'cargo_atual__departamento__id',
        'cargo_atual__nome',
        'nome',
        'id',
        )
    funcionarios_inativos = Funcionario.objects.filter(periodo_trabalhado_corrente=None)
    return render(request, 'frontend/rh/rh-funcionarios.html', locals())
#
@user_passes_test(possui_perfil_acesso_rh)
def funcionarios_relatorios_listar_ativos(request):
    relatorio = True
    funcionarios_ativos = Funcionario.objects.exclude(periodo_trabalhado_corrente=None).order_by('periodo_trabalhado_corrente__inicio')
    return render(request, 'frontend/rh/rh-funcionarios-listar-ativos.html', locals())

#
@user_passes_test(possui_perfil_acesso_rh)
def funcionarios_relatorios_listar_ativos_aniversarios(request):
    mes_especifico = request.GET.get('mes', None)
    # define opções de mes
    dias = []
    for mes_dia in range(1,13):
        dias.append(datetime.date(2013, mes_dia, 1))
    
    if str(mes_especifico).isdigit():
        mes_especifico = int(mes_especifico)
        if 12 >= mes_especifico >= 1:
            meses=[mes_especifico]
    else:
        meses = range(1,13)
    lista = []
    for mes_query in meses:
        funcionarios_ativos = Funcionario.objects.filter(nascimento__month=mes_query).extra(
        #select = {'custom_dt': 'date(nascimento)'}).order_by('-custom_dt'
        select={'birthmonth': 'MONTH(nascimento)', 'brithday': 'DAY(nascimento)'}, order_by=['brithday']
        )
        if funcionarios_ativos:
            lista.append((datetime.date(datetime.date.today().year, mes_query, 1), funcionarios_ativos,))
        relatorio = True
    return render(request, 'frontend/rh/rh-funcionarios-listar-aniversarios.html', locals())
        
#
@user_passes_test(possui_perfil_acesso_rh)
def ver_funcionario(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    if request.POST:
        # folha de ponto
        adicionar_folhaponto_form = AdicionarFolhaDePontoForm(request.POST, request.FILES)
        if adicionar_folhaponto_form.is_valid():
            folha = adicionar_folhaponto_form.save(commit=False)
            folha.periodo_trabalhado = funcionario.periodo_trabalhado_corrente
            # gerente, já vai autorizado
            if request.user.perfilacessorh.gerente:
                folha.autorizado = True
                folha.funcionario_autorizador = request.user.funcionario
            folha.save()            
            folha.funcionario_autorizador = request.user.funcionario
            folha.save()
            messages.success(request, u'Folha de Ponto Adicionada')
        else:
            messages.error(request, u'Formulário para Adicionar Ponto Inválido')

    else:    
        adicionar_folhaponto_form = AdicionarFolhaDePontoForm()
        adicionar_solicitacaolicenca_form = AdicionarSolicitacaoLicencaForm()
        
    return render(request, 'frontend/rh/rh-funcionarios-ver.html', locals())

#
@user_passes_test(possui_perfil_acesso_rh)
def solicitacao_licencas(request,):
    solicitacoes_abertas = SolicitacaoDeLicenca.objects.filter(status="aberta")
    solicitacoes_autorizada = SolicitacaoDeLicenca.objects.filter(status="autorizada")
    return render(request, 'frontend/rh/rh-solicitacao-licencas.html', locals())

#
@user_passes_test(possui_perfil_acesso_rh)
def solicitacao_licenca_add(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    if request.POST:
        form = AdicionarSolicitacaoLicencaForm(request.POST)
        if form.is_valid():
            solicitacao = form.save(commit=False)
            solicitacao.periodo_trabalhado = funcionario.periodo_trabalhado_corrente
            solicitacao.save()
            messages.success(request, u'Sucesso! Solicitação #%s Adicionada' % solicitacao.id)
        else:
            errors = ["%s: %s" % (item[0], str(item[1])) for item in form.errors.items()]
            messages.error(request, "%s" % ' '.join(errors))
    return redirect(reverse('rh:ver_funcionario', args=[funcionario.id,]))

#
@user_passes_test(possui_perfil_acesso_rh)
def solicitacao_licencas_autorizar(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoDeLicenca, pk=solicitacao_id)
    solicitacao.status = "autorizada"
    solicitacao.data_autorizado = datetime.date.today()
    solicitacao.processado_por = request.user.funcionario
    solicitacao.save()
    messages.success(request, u"Sucesso! Solicitação #%s Autorizada" % solicitacao.id)
    return redirect(reverse('rh:solicitacao_licencas'))

#

class SelecionaMesReferencia(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(SelecionaMesReferencia, self).__init__(*args, **kwargs)
        self.fields['dia_referencia'].widget.attrs['class'] = 'datepicker'
    
    dia_referencia = forms.DateField(label=u"Selecione o Mês/Ano de Referência", initial=datetime.date.today())

@user_passes_test(possui_perfil_acesso_rh)
def exames_medicos_relatorios_custos(request):
    if request.POST:
        form_mes_referencia = SelecionaMesReferencia(request.POST)
        if form_mes_referencia.is_valid():
            resultados = True
            data_referencia = form_mes_referencia.cleaned_data['dia_referencia']
            #calcula quantidade de funcionarios ativos
            periodos_trabalhados = PeriodoTrabalhado.objects.filter(
            Q(inicio__lte=data_referencia, fim=None) | \
            Q(inicio__lte=data_referencia, fim__gte=data_referencia)
            )
            valor_exames_mensal_por_ativo = getattr(settings, "VALOR_EXAME_MENSAL_FUNCIONARIO", 4)
            total_mensal_exame = float(periodos_trabalhados.count()) * float(valor_exames_mensal_por_ativo)
            # calcula quantidade de rotinas medicas
            rotinas = RotinaExameMedico.objects.filter(data__month=data_referencia.month, data__year=data_referencia.year, realizado=True)
            total_rotinas = 0
            for rotina in rotinas:
                total_rotinas += rotina.valor_total()
            total_geral = float(total_rotinas) + float(total_mensal_exame)
    else:
        form_mes_referencia = SelecionaMesReferencia()
    return render(request, 'frontend/rh/rh-exames-medicos-relatorios-custos.html', locals())
    

@user_passes_test(possui_perfil_acesso_rh)
def exames_medicos(request):
    exames_data_pendente = RotinaExameMedico.objects.filter(data=None)
    exames_remarcacao = RotinaExameMedico.objects.filter(data__lt=datetime.date.today(), realizado=False)
    exames_agendados = RotinaExameMedico.objects.filter(data__gt=datetime.date.today(), realizado=False)
    exames_realizados = RotinaExameMedico.objects.filter(realizado=True)
    return render(request, 'frontend/rh/rh-exames-medicos.html', locals())

#
@user_passes_test(possui_perfil_acesso_rh)
def exames_medicos_ver(request, exame_id):
    exame = get_object_or_404(RotinaExameMedico, id=exame_id)
    if 'agendar' in request.POST:
        form_agendar = AgendarExameMedicoForm(request.POST, instance=exame)
        if form_agendar.is_valid():
            exame = form_agendar.save()
            messages.info(request, u"Agendado para %s" % exame.data.strftime("%d/%m/%Y %H:%M"))
    else:
        form_agendar = AgendarExameMedicoForm(instance=exame)
    exame_arquivo_form = AdicionarArquivoRotinaExameForm(instance=exame)
    
    return render(request, 'frontend/rh/rh-exames-medicos-ver.html', locals())

#
@user_passes_test(possui_perfil_acesso_rh)
def exames_medicos_exame_realizado_hoje(request, exame_id):
    '''marca exame como Realizado Hoje'''
    exame = get_object_or_404(RotinaExameMedico, pk=exame_id)
    if request.POST:
        form = AdicionarArquivoRotinaExameForm(request.POST, request.FILES, instance=exame)
        if form.is_valid():            
            try:
                exame_alterado = form.save(commit=False)
                exame_alterado.realizado = True
                exame_alterado.save()
                messages.success(request, u"Exame marcado como Realizado!")
                # Se é exame admissional, ou atualização ou mudança de cargo
                # marcar para daqui a X dias o exame de atualização
                if exame_alterado.tipo in ["a", "u", "p"]:
                    dias_proximo_exame = exame_alterado.periodo_trabalhado.funcionario.cargo_atual.dias_renovacao_exames
                    data_novo_exame = datetime.date.today() + relativedelta( days = dias_proximo_exame )
                    novo_exame = exame.periodo_trabalhado.rotinaexamemedico_set.create(
                        tipo="u",
                        data=data_novo_exame,
                        periodo_trabalhado=exame.periodo_trabalhado,
                    )
                    messages.info(request, u"Um Novo Exame do Tipo %s foi Criado: #ID%s" % (novo_exame.get_tipo_display(), novo_exame.id))
                    # adiciona os exames padrao para o cargo do funcionario
                    for exame_padrao in exame.periodo_trabalhado.funcionario.cargo_atual.exame_medico_padrao.all():
                        novo_exame.exames.add(exame_padrao)
                    novo_exame.save()

            except ValidationError, e:
                messages.error(request, "%" '; '.join(e.messages))        
            except:
                raise
        else:
            errors = ["%s: %s" % (item[0], str(item[1])) for item in form.errors.items()]
            messages.error(request, "%" '; '.join(errors))

    return redirect(reverse('rh:exames_medicos_ver', args=[exame.id,]))

#
@user_passes_test(possui_perfil_acesso_rh)
def processos_admissao(request):
    processos_admissao_ativos = PeriodoTrabalhado.objects.filter(fim=None)
    processos_admissao_inativos = PeriodoTrabalhado.objects.exclude(fim=None)
    return render(request, 'frontend/rh/rh-processos-admissao.html', locals())
# FORM ADMITIR FUNCIONARIO
#
class FormAdmitirFuncionario(forms.ModelForm):
    
    periodo_trabalhado_inicio = forms.DateField(label="Data de Admissão")
    
    def __init__(self, *args, **kwargs):
        super(FormAdmitirFuncionario, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            if key not in 'complemento':
                self.fields[key].required = True
        self.fields['carteira_profissional_emissao'].widget.attrs['class'] = 'datepicker'
        self.fields['rg_data'].widget.attrs['class'] = 'datepicker'
        self.fields['nascimento'].widget.attrs['class'] = 'datepicker'
        self.fields['periodo_trabalhado_inicio'].widget.attrs['class'] = 'datepicker'
        self.fields['cargo_inicial'].widget.attrs['class'] = 'select2'
        
    
    class Meta:
        model = Funcionario
        fields = (
            'nome',
            'foto',
            'nascimento',
            'salario_inicial',
            'carteira_profissional_numero',
            'carteira_profissional_serie',
            'carteira_profissional_emissao',
            'rg',
            'rg_data',
            'rg_expeditor',
            'cpf',
            'pis',
            'estado_civil',
            'escolaridade_nivel',
            'bairro',
            'cep',
            'rua',
            'numero',
            'complemento',
            'cargo_inicial',
            'endereco_empresa_designado',
        )
#
@user_passes_test(possui_perfil_acesso_rh)
def processos_admissao_admitir(request):
    admitir=True
    form_admitir_funcionario = FormAdmitirFuncionario()
    if request.POST:
        form_admitir_funcionario = FormAdmitirFuncionario(request.POST, request.FILES)
        if form_admitir_funcionario.is_valid():
            novo_funcionario = form_admitir_funcionario.save()
            # cria o periodo trabalhado
            novo_periodo_trabalhado = PeriodoTrabalhado.objects.create(
                funcionario=novo_funcionario,
                inicio=form_admitir_funcionario.cleaned_data['periodo_trabalhado_inicio']
            )
            novo_funcionario.periodo_trabalhado_corrente = novo_periodo_trabalhado
            novo_funcionario.save()
            messages.success(request, u"Sucesso! Novo funcionário (%s) criado/admitido." % novo_funcionario)
        
    return render(request, 'frontend/rh/rh-processos-admissao-admitir.html', locals())
#
@user_passes_test(possui_perfil_acesso_rh)
def processos_demissao(request):
    processos_abertos = Demissao.objects.filter(status="andamento")
    processos_fechados = Demissao.objects.filter(status="finalizado")
    return render(request, 'frontend/rh/rh-processos-demissao.html', locals())

@user_passes_test(possui_perfil_acesso_rh)
def processos_demissao_finalizar(request, processo_id):
    processo = get_object_or_404(Demissao, pk=processo_id)
    if request.POST and request.FILES.get('termo_recisorio', None):
        processo.termo_recisorio = request.FILES['termo_recisorio']
    else:
        processo.termo_recisorio = None
    processo.status = u'finalizado'
    processo.save()
    messages.info(request, u"Processo Finalizado.")
    return redirect(reverse("rh:processos_demissao"))

#
@user_passes_test(possui_perfil_acesso_rh)
def demitir_funcionario(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    # Se não possuir periodo corrente, não pode ser demitido
    if not funcionario.periodo_trabalhado_corrente:
        messages.warning(request, u"Impossível demitir este Funcionário. Ele não possui Período Trabalhado Corrente")
        return redirect(reverse('rh:ver_funcionario', args=[funcionario.id,]))
    if request.POST:
        form = DemitirFuncionarioForm(request.POST)
        if form.is_valid():
            data_exame_demissional = form.cleaned_data['exame_demissional']
            periodo_trabalhado_finalizado = funcionario.periodo_trabalhado_corrente
            # encerra Periodo Trabalhado Corrente e desvincula ao funcionario
            funcionario.periodo_trabalhado_corrente.fim = datetime.date.today()
            funcionario.periodo_trabalhado_corrente.save()
            messages.info(request, u'Período Trabalhado Finalizado')
            # remove todos os exames não realizados
            funcionario.periodo_trabalhado_corrente.rotinaexamemedico_set.filter(realizado=False).delete()
            messages.info(request, u'Exames Médicos Futuros Cancelados')
            # agenda rotina de médico demissional com padrões do cargo
            # caso seja funcionario em periodo de experiencia, nao precisa de demissional
            if periodo_trabalhado_finalizado.periodo_experiencia():
                messages.info(request, u'Exame Médico Demissional NÃO CRIADO. Funcionário me período de Experiência: %s' % periodo_trabalhado_finalizado.dias_trabalhados())
            else:
                exame = funcionario.periodo_trabalhado_corrente.rotinaexamemedico_set.create(
                    data=data_exame_demissional,
                    tipo='d',
                    periodo_trabalhado=periodo_trabalhado_finalizado,
                )
                for exame_padrao in funcionario.cargo_atual.exame_medico_padrao.all():
                    exame.exames.add(exame_padrao)
                exame.save()
                messages.info(request, u'Exame Médico Demissional criado em: %s, #ID%s' % (exame.data, exame.id))
            
            # Cria Registro de Demissão
            demissao = funcionario.demissao_set.create(
                data=datetime.date.today(),
                periodo_trabalhado_finalizado=periodo_trabalhado_finalizado,
                demissor=request.user.funcionario,
            )
            messages.info(request, u'Entrada de Demissão Criada: ID#%s' % demissao.id)
            # sucesso no processo
            funcionario.periodo_trabalhado_corrente = None
            funcionario.save()
            messages.info(request, u'Período Trabalhado Desvinculado como Corrente')
            messages.success(request, u'Processo de Demissão Iniciado com Sucesso!')
            # redireciona pra tela do usuário
            return redirect(reverse('rh:ver_funcionario', args=[funcionario.id,]))
        else:
            messages.error(request, u'Erro de Validação do Formulário % s' % form.errors)
            
    else:
        form = DemitirFuncionarioForm()
    return render(request, 'frontend/rh/rh-funcionarios-demitir.html', locals())


#
# FORM PROMOVER FUNCIONARIO
#
class FormPromoverFuncionario(forms.Form):
    
    def clean(self):
        cleaned_data = super(FormPromoverFuncionario, self).clean()
        if not self.cleaned_data['novo_cargo'] and not self.cleaned_data['novo_valor_salarial']:
            raise ValidationError(u"Pelo menos uma promoção deve ser realizada: Cargo ou Salário")
        return cleaned_data
    
    def clean_data_promocao(self):
        data = self.cleaned_data['data_promocao']
        if data < datetime.date.today():
            raise ValidationError(u"Data tem que ser no futuro ou igual a hoje.")
        if data < self.atribuicao.inicio:
            raise ValidationError(u"Data tem que ser maior que o início da última atribuição de cargo, %s" % self.atribuicao.inicio)
            return self.atribuicao.inicio
        return data
    
    def __init__(self, *args, **kwargs):
        self.atribuicao = kwargs.pop('atribuicao', None)
        super(FormPromoverFuncionario, self).__init__(*args, **kwargs)
        self.fields['novo_cargo'].widget.attrs['class'] = 'select2'
        self.fields['novo_cargo'].queryset = Cargo.objects.all().exclude(id=self.atribuicao.cargo.id)
        self.fields['data_promocao'].widget.attrs['class'] = 'datepicker'

    data_promocao = forms.DateField(initial=datetime.date.today(), label=u"Data de Promoção")
    # cargo
    novo_cargo = forms.ModelChoiceField(queryset=[], required=False)
    observacao_cargo = forms.CharField(widget=forms.Textarea, required=False)
    # salario
    novo_valor_salarial = forms.DecimalField(max_digits=15, decimal_places=2, required=False)
    observacao_salarial = forms.CharField(widget=forms.Textarea, required=False)

# promover
@user_passes_test(possui_perfil_acesso_rh)
def promover_funcionario(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    # pega a atribuicao de cargo atual, ou se cria
    if funcionario.periodo_trabalhado_corrente:
        created, atribuicao = funcionario.periodo_trabalhado_corrente.atribuicao_atual()
        if atribuicao:
            if created:
                messages.warning(request, u"Atenção! Funcionário não possuía Atribuição de Cargo!")
                messages.success(request, u"Sucesso! Atribuição criada para Cargo %s, Início: %s" % (atribuicao.cargo, atribuicao.inicio))
            # agora deve mostrar o form da atribuicao atual, descobrir o cargo de destino
            # ao processar o formulario, criado a próxima atribuição
            form_promover = FormPromoverFuncionario(atribuicao=atribuicao)
            if request.POST:
                form_promover = FormPromoverFuncionario(request.POST, atribuicao=atribuicao)
                if form_promover.is_valid():
                    # data promocao
                    data_promocao = form_promover.cleaned_data['data_promocao']
                    # promocao salarial
                    novo_valor = form_promover.cleaned_data['novo_valor_salarial']
                    novo_cargo = form_promover.cleaned_data['novo_cargo']
                    # novos valores
                    if novo_valor:
                        if funcionario.salario():
                            valor_origem = funcionario.salario()
                        else:
                            valor_origem = novo_valor
                        # cria instancia do PromocaoSalarial
                        observacao_salarial = form_promover.cleaned_data['observacao_salarial']
                        promocao_salarial = funcionario.promocao_salarial_set.create(
                            data_promocao=data_promocao,
                            atribuicao_de_cargo=atribuicao,
                            valor_destino=novo_valor,
                            valor_origem=valor_origem,
                            solicitante=request.user.funcionario,
                            autorizador=request.user.funcionario,
                            periodo_trabalhado=funcionario.periodo_trabalhado_corrente,
                            observacao=observacao_salarial,
                            # opcoes para fazer com passo de autorizacao
                            aprovado=True,
                            avaliado=True,
                            data_resolucao=datetime.date.today(),
                            criado_por=request.user.funcionario, 
                        )
                        messages.success(request, u'Sucesso! Nova Promoção Salarial #%s Criada para %s' % (promocao_salarial.id, funcionario))
                        # recalcula o valor hora
                        valor_hora_anterior = funcionario.valor_hora
                        funcionario.calcular_valor_hora()
                        messages.info(request, u'Informação: Valor Hora Recalculado: %s -> %s' % (valor_hora_anterior, funcionario.valor_hora))
                    if novo_cargo:
                        # fecha a atribuicao de cargo atual
                        atribuicao.fim = data_promocao
                        atribuicao.save()
                        atribuicao_origem = atribuicao
                        messages.info(request, u'Informação: Atribuição de Cargo #%s: %s Fechada em %s' % (atribuicao_origem.id, atribuicao_origem.cargo, atribuicao_origem.fim))
                        # cria nova atribuicao, com inciio para 1 dia após origem
                        atribuicao_destino = funcionario.periodo_trabalhado_corrente.atribuicaodecargo_set.create(
                            cargo=novo_cargo,
                            inicio=data_promocao + datetime.timedelta(days=1),
                            criado_por=request.user.funcionario, 
                            local_empresa=funcionario.endereco_empresa_designado
                        )
                        messages.info(request, u'Informação: Nova Atribuição de Cargo #%s: %s Aberta!' % (atribuicao_destino.id, atribuicao_destino.cargo))
                        # cria a instancia do PromocaoCargo
                        observacao_cargo = form_promover.cleaned_data['observacao_cargo']
                        promocao_cargo = funcionario.promocao_cargo_set.create(
                            data_promocao=data_promocao,
                            atribuicao_de_origem=atribuicao_origem,
                            atribuicao_de_destino=atribuicao_destino,
                            periodo_trabalhado=funcionario.periodo_trabalhado_corrente,
                            solicitante=request.user.funcionario,
                            autorizador=request.user.funcionario,
                            observacao=observacao_cargo,
                            criado_por=request.user.funcionario, 
                            # opcoes para fazer com passo de autorizacao
                            aprovado=True,
                            avaliado=True,
                            data_resolucao=datetime.date.today(),
                        )
                        # apaga todos os exames não realizados (provavelmente somente exame periodico)
                        funcionario.periodo_trabalhado_corrente.rotinaexamemedico_set.filter(realizado=False).delete()
                        # gera novo exame do tipo promoção
                        exame = funcionario.periodo_trabalhado_corrente.rotinaexamemedico_set.create(
                            tipo='p',
                        )
                        for exame_padrao in novo_cargo.exame_medico_padrao.all():
                            exame.exames.add(exame_padrao)
                        exame.save()
                        messages.success(request, u"Promoção de Cargo Registrada: #%s para %s" % (promocao_cargo, promocao_cargo.beneficiario))
                    # retorna para lista de promoções
                    return redirect(reverse("rh:ver_funcionario", args=[funcionario.id]))

    else:
        message.error(request, u"Erro. Funcionário não possui perído ativo corrente!")
    return render(request, 'frontend/rh/rh-funcionarios-promover.html', locals())

# lista promocoes
@user_passes_test(possui_perfil_acesso_rh)
def processos_promocao(request):
    processos_cargo = PromocaoCargo.objects.all()
    processos_salarial = PromocaoSalario.objects.all()    
    return render(request, 'frontend/rh/rh-processos-promocao.html', locals())

#
# CAPACITACAO DE PROCEDIMENTOS
#
@user_passes_test(possui_perfil_acesso_rh)
def capacitacao_de_procedimentos(request):
    # para todos os funcioários ativos
    funcionarios_ativos = Funcionario.objects.all().exclude(periodo_trabalhado_corrente=None).order_by('cargo_atual__departamento__nome', 'cargo_atual__nome')
    funcionarios_ativos_valores =  funcionarios_ativos.values(
        'cargo_atual__departamento__nome',
        'cargo_atual__departamento__id',
        'cargo_atual__nome',
        'nome',
        'id',
        )
    return render(request, 'frontend/rh/rh-capacitacao-de-procedimentos.html', locals())

#
@user_passes_test(possui_perfil_acesso_rh)
def capacitacao_de_procedimentos_gerar_ar(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    subprocedimentos_id = request.GET.get('subprocedimentos')
    tipo = request.GET.get('tipo')
    if tipo == 'adicionar':
        tipo_treino = 'adicionar'
    elif tipo == 'atualizar':
        tipo_treino = 'atualizar'
    else:
        tipo_treino = 'adicionar'
    if subprocedimentos_id:
        subprocedimentos_id_list = subprocedimentos_id.split(',')
        subprocedimentos = SubProcedimento.objects.filter(id__in=subprocedimentos_id_list)
        ar = AtribuicaoDeResponsabilidade.objects.create(
             periodo_trabalhado=funcionario.periodo_trabalhado_corrente,
             criado_por=request.user.funcionario,
             tipo_de_treinamento=tipo_treino,
        )
        ar.subprocedimentos = subprocedimentos
        ar.save()
        return render(request, 'frontend/rh/rh-capacitacao-gerar-atribuicao-de-responsabilidade-imprimir.html', locals())
    else:
        messages.info(request, 'Nenhum Procedimento escolhido para %s' % funcionario)
        return redirect(reverse("rh:capacitacao_de_procedimentos"))
        

#
@user_passes_test(possui_perfil_acesso_rh)
def capacitacao_de_procedimentos_ver_ar(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    tipo =  request.GET.get('tipo', 'adicionar')
    if tipo == 'adicionar':
        atribuicoes = funcionario.atribuicao_responsabilidade_nao_treinado_adicionar()
    elif tipo == 'atualizar':
        atribuicoes = funcionario.atribuicao_responsabilidade_nao_treinado_atualizar()

    if not tipo or not atribuicoes:
        messages.info(request, 'Nenhuma Atribuição de Responsabilidade para %s. É Preciso gerar uma nova.' % funcionario)
        return redirect(reverse("rh:capacitacao_de_procedimentos"))
    return render(request, 'frontend/rh/rh-capacitacao-ver-atribuicao-de-responsabilidade.html', locals())

@user_passes_test(possui_perfil_acesso_rh)
def capacitacao_de_procedimentos_remover_ar(request, funcionario_id, atribuicao_responsabilidade_id):
    tipo = request.GET.get('tipo', 'adicionar')
    atribuicao = get_object_or_404(AtribuicaoDeResponsabilidade, id=atribuicao_responsabilidade_id, periodo_trabalhado__funcionario__id=funcionario_id)
    atribuicao.delete()
    messages.success(request, u"Sucesso! Atribuição de Responsabilidade removida.")
    return redirect(reverse("rh:capacitacao_de_procedimentos_ver_ar", args=[funcionario_id,])+"?tipo=%s" % tipo)

class FormConfirmaAtribuicaoDeResponsabilidade(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(FormConfirmaAtribuicaoDeResponsabilidade, self).__init__(*args, **kwargs)
        self.fields['data_treinado'].widget.attrs['class'] = 'input-small datepicker'
        self.fields['data_treinado'].label = "Data de Treinamento"
        self.fields['horas_treinadas'].required = True
    
    class Meta:
        model = AtribuicaoDeResponsabilidade
        fields = 'horas_treinadas', 'data_treinado'

@user_passes_test(possui_perfil_acesso_rh)
def capacitacao_de_procedimentos_confirmar(request, funcionario_id, atribuicao_responsabilidade_id):
    atribuicao = get_object_or_404(AtribuicaoDeResponsabilidade, id=atribuicao_responsabilidade_id, periodo_trabalhado__funcionario__id=funcionario_id)
    atribuicao.data_treinado = datetime.date.today()
    form_atribuicao = FormConfirmaAtribuicaoDeResponsabilidade(instance=atribuicao)
    if request.POST:
        form_atribuicao = FormConfirmaAtribuicaoDeResponsabilidade(request.POST, instance=atribuicao)
        if form_atribuicao.is_valid():
            # verificar se existe a capacitacao deste funcionario
            for subprocedimento in form_atribuicao.instance.subprocedimentos.all():
                # pega ou cria a Capacitacao
                capacitacao,created = CapacitacaoDeSubProcedimento.objects.get_or_create(
                    periodo_trabalhado = atribuicao.periodo_trabalhado,
                    subprocedimento=subprocedimento
                )
                if created:
                    # eh uma capacitacao nova!
                    messages.info(request, u'Uma nova Capacitação de Responsabilidade foi criada.')
                else:
                    messages.info(request, u'Atualizando Capacitação de Responsabilidade.')
                #
                capacitacao.versao_treinada = subprocedimento.versao
                capacitacao.ultima_atualizacao = form_atribuicao.cleaned_data['data_treinado']
                capacitacao.save()
                # salva a atribuicao
                atribuicao = form_atribuicao.save(commit=False)
                # define quem e quando se confirmou a atribuicao
                atribuicao.confirmado_por = request.user.funcionario
                atribuicao.confirmado_data = datetime.datetime.now()
                atribuicao.treinamento_realizado = True
                # salva
                atribuicao.save()
                messages.success(request, u'Atribuição de Responsabilidade Salva')
                return redirect(reverse("rh:capacitacao_de_procedimentos"))
    return render(request, 'frontend/rh/rh-capacitacao-atribuicao-de-responsabilidade-confirmar.html', locals())

#
#CONTROLES DO FUNCIONARIO
#
# controle_de_ferias
@user_passes_test(possui_perfil_acesso_rh)
def controle_de_ferias(request):
    funcionarios = Funcionario.objects.exclude(periodo_trabalhado_corrente=None)
    return render(request, 'frontend/rh/rh-controle-de-ferias.html', locals())

# controle_de_banco_de_horas
@user_passes_test(possui_perfil_acesso_rh)
def controle_de_banco_de_horas(request):
    funcionarios = Funcionario.objects.exclude(periodo_trabalhado_corrente=None)
    horas_extra_autorizadas = AutorizacaoHoraExtra.objects.filter(
        data_execucao__month=datetime.date.today().month,
        data_execucao__year=datetime.date.today().year,
    )
    return render(request, 'frontend/rh/rh-controle-de-banco-de-horas.html', locals())

# controle_banco_de_horas_do_funcionario
@user_passes_test(possui_perfil_acesso_rh)
def controle_banco_de_horas_do_funcionario(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    folhas_abertas = funcionario.periodo_trabalhado_corrente.folhadeponto_set.filter(encerrado=False)
    folhas_fechadas = funcionario.periodo_trabalhado_corrente.folhadeponto_set.filter(encerrado=True)
    # processo adicionar entrada folha
    if request.POST:
        form_add_entrada_folha_ponto = AdicionarEntradaFolhaDePontoForm(request.POST)
        if form_add_entrada_folha_ponto.is_valid():
            entrada = form_add_entrada_folha_ponto.save(commit=False)
            folha_id = int(form_add_entrada_folha_ponto.data['folha'])
            folha = get_object_or_404(FolhaDePonto, id=folha_id)
            entrada.folha = folha
            entrada.adicionado_por = request.user.funcionario
            entrada.save()
            messages.success(request, u'Sucesso: Lançamento de %s horas realizado!' % entrada.total )
        else:
            messages.error(request, u'Formulário Não Validado')
            
    else:
        form_add_entrada_folha_ponto = AdicionarEntradaFolhaDePontoForm()
    return render(request, 'frontend/rh/rh-banco-de-horas-funcionario.html', locals())

#
@user_passes_test(possui_perfil_acesso_rh)
def controle_banco_de_horas_do_funcionario_gerenciar(request, funcionario_id, folha_id):
    folha = get_object_or_404(FolhaDePonto, periodo_trabalhado__funcionario__id=funcionario_id, id=folha_id)
    folha.encerrado = True
    folha.save()
    return redirect(reverse('rh:controle_banco_de_horas_do_funcionario', args=[folha.periodo_trabalhado.funcionario.id,]))

# matriz de competencia
@user_passes_test(possui_perfil_acesso_rh)
def matriz_de_competencias(request):
    competencias = Competencia.objects.all()
    return render(request, 'frontend/rh/rh-matriz-de-competencias.html', locals())


# HORA EXTRA FORM
class AdicionarHoraExtraForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        periodo_trabalhado = kwargs.pop('periodo_trabalhado', None)
        super(AdicionarHoraExtraForm, self).__init__(*args, **kwargs)
        self.fields['periodo_trabalhado'].widget = forms.HiddenInput()
        self.fields['periodo_trabalhado'].initial = periodo_trabalhado
        self.fields['data_execucao'].widget.attrs['class'] = 'datepicker'
        
    
    class Meta:
        model = AutorizacaoHoraExtra
        fields = 'periodo_trabalhado', 'quantidade', 'data_execucao',

# adicionar hora extra
@user_passes_test(possui_perfil_acesso_rh)
def adicionar_hora_extra(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    valor_hora = funcionario.calcular_valor_hora()
    form = AdicionarHoraExtraForm(periodo_trabalhado=funcionario.periodo_trabalhado_corrente)
    if request.POST:
        form = AdicionarHoraExtraForm(request.POST, periodo_trabalhado=funcionario.periodo_trabalhado_corrente)
        if form.is_valid():
            autorizacao = form.save(commit=False)
            autorizacao.solicitante = request.user.funcionario
            valor_hora = funcionario.calcular_valor_hora()
            autorizacao.valor_total = autorizacao.quantidade * valor_hora
            autorizacao.save()
            messages.success(request, u"Sucesso! Autorização de Hora Extra de %s horas (R$ %s) para %s criado" % (autorizacao.quantidade, autorizacao.valor_total, autorizacao.periodo_trabalhado.funcionario))
            form = AdicionarHoraExtraForm(periodo_trabalhado=funcionario.periodo_trabalhado_corrente)
    return render(request, 'frontend/rh/rh-hora-extra-adicionar.html', locals())


@user_passes_test(possui_perfil_acesso_rh)
def imprimir_hora_extra(request, funcionario_id, autorizacao_hora_extra_id):
    autorizacao = get_object_or_404(
        AutorizacaoHoraExtra,
        id=autorizacao_hora_extra_id,
        periodo_trabalhado__funcionario__id=funcionario_id
    )
    return render(request, 'frontend/rh/rh-hora-extra-imprimir.html', locals())



# FORMS CONTROLES DE FERRAMENTA E EPI
class FormFiltrarControleDeFerramentas(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(FormFiltrarControleDeFerramentas, self).__init__(*args, **kwargs)
        self.fields['funcionario'].widget.attrs['class'] = 'select2'
        self.fields['funcionario'].empty_label = None
    
    funcionario = forms.ModelChoiceField(queryset=Funcionario.objects.all().exclude(periodo_trabalhado_corrente=None), required=True)

#
class FormControleFerramentasAdicionar(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        tipo = kwargs.pop('tipo', None)
        super(FormControleFerramentasAdicionar, self).__init__(*args, **kwargs)
        self.fields['tipo'].initial = tipo
        self.fields['tipo'].widget = forms.HiddenInput()
        #self.fields['funcionario'] = EscolhaDeFuncionario()
        self.fields['funcionario'].widget.attrs['class'] = 'select2'
        self.fields['funcionario'].queryset = Funcionario.objects.all().exclude(periodo_trabalhado_corrente=None).order_by('nome')
    
    class Meta:
        model = ControleDeEquipamento
        fields = 'funcionario', 'observacao', 'tipo'

#
class LinhaControleEquipamentoForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(LinhaControleEquipamentoForm, self).__init__(*args, **kwargs)
        self.fields['produto'].widget = forms.HiddenInput()
        self.fields['produto'].widget.attrs['class'] = 'select2-ajax'
        self.fields['quantidade'].required=True
        self.fields['quantidade'].widget.attrs['class'] = 'input-mini'
        self.fields['codigo_ca'].widget.attrs['class'] = 'input-mini'
        self.fields['data_previsao_devolucao'].widget.attrs['class'] = 'input-small datepicker'
    class Meta:
        model = LinhaControleEquipamento
        fields = 'produto', 'quantidade', 'codigo_ca', 'data_previsao_devolucao'

#
class FormVincularArquivoControle(forms.ModelForm):

    class Meta:
        model = ControleDeEquipamento
        fields = 'arquivo_impresso_assinado',


#
class FormReagendaFerramentaPendente(forms.Form):
    
    def clean_data_de_reagendamento(self):
        data = self.cleaned_data['data_de_reagendamento']
        if data < datetime.date.today():
            raise forms.ValidationError('Data deve ser no futuro.')
        return data
    
    def __init__(self, *args, **kwargs):
        super(FormReagendaFerramentaPendente, self).__init__(*args, **kwargs)
        self.fields['data_de_reagendamento'].widget.attrs['class'] = 'datepicker'
    
    
    data_de_reagendamento = forms.DateField()

#
# CONTROLE DE FERRAMENTAS
#
@user_passes_test(possui_perfil_acesso_rh)
def controle_de_ferramenta(request):
    form_filtra_ferramentas = FormFiltrarControleDeFerramentas()
    form_reagenda_feramenta = FormReagendaFerramentaPendente() 
    if request.POST:
        form_filtra_ferramentas = FormFiltrarControleDeFerramentas(request.POST)
        if form_filtra_ferramentas.is_valid():
            funcionario = form_filtra_ferramentas.cleaned_data['funcionario']
            controles_do_funcionario = ControleDeEquipamento.objects.filter(funcionario=funcionario, tipo="ferramenta").order_by('criado')

    controles_sem_arquivos = ControleDeEquipamento.objects.filter(arquivo_impresso_assinado='', tipo="ferramenta")
    linhas_com_devolucao_vencida = LinhaControleEquipamento.objects.filter(
            controle__tipo="ferramenta",
            data_devolvido=None,
            data_previsao_devolucao__lt=datetime.date.today()
    ).order_by('controle__criado', 'data_previsao_devolucao')
    return render(request, 'frontend/rh/rh-controle-de-ferramenta.html', locals())

#
@user_passes_test(possui_perfil_acesso_rh)
def controle_de_ferramenta_adicionar(request):
    # form do controle
    form_adicionar = FormControleFerramentasAdicionar(tipo="ferramenta")
    quantidade_adicionar = request.POST.get('quantidade_adicionar', 1)
    # form dos produtos vinculados
    LinhaDeEquipamentoFormset = forms.models.inlineformset_factory(
        ControleDeEquipamento,
        LinhaControleEquipamento,
        extra=0,
        can_delete=False,
        form=LinhaControleEquipamentoForm,
    )
    linha_equipamento_form = LinhaDeEquipamentoFormset(prefix="linhaequipamento")
    if request.POST:
        if 'adicionar-campos-btn' in request.POST:
            cp = request.POST.copy()
            quantidade_adicionar = request.POST.get('quantidade_adicionar', 1)
            if quantidade_adicionar == '':
                quantidade_adicionar = 1
            else:
                quantidade_adicionar = int(quantidade_adicionar)
            cp['linhaequipamento-TOTAL_FORMS'] = int(cp['linhaequipamento-TOTAL_FORMS'])+ quantidade_adicionar
            # devolve o form processado
            linha_equipamento_form = LinhaDeEquipamentoFormset(cp, prefix="linhaequipamento")
            form_adicionar = FormControleFerramentasAdicionar(cp, tipo="epi")
        if 'criar-controle-btn' in request.POST:
            linha_equipamento_form = LinhaDeEquipamentoFormset(request.POST, prefix="linhaequipamento")
            form_adicionar = FormControleFerramentasAdicionar(request.POST, tipo="ferramenta")
            if form_adicionar.is_valid() and linha_equipamento_form.is_valid():
                controle = form_adicionar.save(commit=False)
                controle.criado_por = request.user.funcionario
                controle.save()
                for linha_form in linha_equipamento_form:
                        linha = linha_form.save(commit=False)
                        try:
                            # usuario pediu os campos mas não usou, usando
                            # try ele desconsidera e nao salva
                            produto = linha.produto
                            linha.controle = controle
                            linha.data_entregue = datetime.date.today()
                            linha.produto=produto
                            linha.save()
                        except:
                            pass
                messages.success(request, "Sucesso! Novo Controle #%s criado" % controle.id)
                return redirect(reverse("rh:controle_de_ferramenta"))
    return render(request, 'frontend/rh/rh-controle-de-ferramenta-adicionar.html', locals())



#
@user_passes_test(possui_perfil_acesso_rh)
def controle_de_ferramenta_imprimir(request, controle_id):
    controle = get_object_or_404(ControleDeEquipamento, pk=controle_id)
    local_padrao = getattr(settings, 'LOCAL_PADRAO_DOCUMENTOS', u'Teófilo Otoni, Minas Gerais')
    nome_empresa_completo = getattr(settings, 'NOME_EMPRESA_COMPLETO', u'NOME DA EMPRESA LTDA.')
    total_do_controle = 0
    for linha in controle.linhacontroleequipamento_set.all():
        total_do_controle += (linha.quantidade * linha.produto.preco_consumo)
    return render(request, 'frontend/rh/rh-controle-de-ferramenta-imprimir.html', locals())
#
@user_passes_test(possui_perfil_acesso_rh)
def controle_de_ferramenta_vincular_arquivo(request, controle_id):
    controle = get_object_or_404(ControleDeEquipamento, pk=controle_id)
    form_vincular = FormVincularArquivoControle(instance=controle)
    if request.POST:
        form_vincular = FormVincularArquivoControle(request.POST, request.FILES, instance=controle)
        if form_vincular.is_valid():
            controle = form_vincular.save(commit=False)
            controle.data_arquivo_impresso_assinado_recebido = datetime.date.today()
            controle.receptor_arquivo_impresso = request.user.funcionario
            controle.save()
            messages.success(request, "Arquivo de Controle de Ferramenta #%s salvo com sucesso!" % controle.id)
            return redirect(reverse("rh:controle_de_ferramenta"))
    return render(request, 'frontend/rh/rh-controle-de-ferramenta-vincular-arquivo.html', locals())
#
@user_passes_test(possui_perfil_acesso_rh)
def controle_de_ferramenta_retornar(request, controle_id, linha_id):
    linha = get_object_or_404(LinhaControleEquipamento, pk=linha_id, controle__id=controle_id)
    linha.data_devolvido = datetime.date.today()
    linha.funcionario_receptor = request.user.funcionario
    linha.save()
    messages.success(request, u"Sucesso! Linha de Equipamento de Ferramenta #%s marcado como entregue." % linha.id)
    return redirect(reverse('rh:controle_de_ferramenta') + "#retorno-equipamento-pendente")
#
# CONTROLE DE EPI 
#
@user_passes_test(possui_perfil_acesso_rh)
def controle_de_epi(request):
    form_filtra_epi = FormFiltrarControleDeFerramentas()
    if request.POST:
        form_filtra_epi = FormFiltrarControleDeFerramentas(request.POST)
        if form_filtra_epi.is_valid():
            funcionario = form_filtra_epi.cleaned_data['funcionario']
            controles_do_funcionario = ControleDeEquipamento.objects.filter(funcionario=funcionario, tipo="epi").order_by('criado')

    controles_sem_arquivos = ControleDeEquipamento.objects.filter(arquivo_impresso_assinado='', tipo="epi")
    linhas_com_devolucao_vencida = LinhaControleEquipamento.objects.filter(
            controle__tipo="epi",
            data_devolvido=None,
            data_previsao_devolucao__lt=datetime.date.today()
    ).order_by('controle__criado', 'data_previsao_devolucao')
    return render(request, 'frontend/rh/rh-controle-de-epi.html', locals())

#
@user_passes_test(possui_perfil_acesso_rh)
def controle_de_epi_adicionar(request):
    # form do controle
    form_adicionar = FormControleFerramentasAdicionar(tipo="epi")
    quantidade_adicionar = request.POST.get('quantidade_adicionar', 1)
    # form dos produtos vinculados
    LinhaDeEquipamentoFormset = forms.models.inlineformset_factory(
        ControleDeEquipamento,
        LinhaControleEquipamento,
        extra=0,
        can_delete=False,
        form=LinhaControleEquipamentoForm,
    )
    linha_equipamento_form = LinhaDeEquipamentoFormset(prefix="linhaequipamento")
    if request.POST:
        if 'adicionar-campos-btn' in request.POST:
            cp = request.POST.copy()
            quantidade_adicionar = request.POST.get('quantidade_adicionar', 1)
            if quantidade_adicionar == '':
                quantidade_adicionar = 1
            else:
                quantidade_adicionar = int(quantidade_adicionar)
            cp['linhaequipamento-TOTAL_FORMS'] = int(cp['linhaequipamento-TOTAL_FORMS'])+ quantidade_adicionar
            # devolve o form processado
            linha_equipamento_form = LinhaDeEquipamentoFormset(cp, prefix="linhaequipamento")
            form_adicionar = FormControleFerramentasAdicionar(cp, tipo="epi")
        if 'criar-controle-btn' in request.POST:
            linha_equipamento_form = LinhaDeEquipamentoFormset(request.POST, prefix="linhaequipamento")
            form_adicionar = FormControleFerramentasAdicionar(request.POST, tipo="epi")
            if form_adicionar.is_valid() and linha_equipamento_form.is_valid():
                controle = form_adicionar.save(commit=False)
                controle.criado_por = request.user.funcionario
                controle.save()
                for linha_form in linha_equipamento_form:
                        linha = linha_form.save(commit=False)
                        try:
                            # usuario pediu os campos mas não usou, usando
                            # try ele desconsidera e nao salva
                            produto = linha.produto
                            linha.controle = controle
                            linha.produto=produto
                            linha.save()
                        except:
                            pass
                messages.success(request, "Sucesso! Novo Controle #%s criado" % controle.id)
                return redirect(reverse("rh:controle_de_epi"))
    return render(request, 'frontend/rh/rh-controle-de-epi-adicionar.html', locals())



#
@user_passes_test(possui_perfil_acesso_rh)
def controle_de_epi_imprimir(request, controle_id):
    controle = get_object_or_404(ControleDeEquipamento, pk=controle_id)
    local_padrao = getattr(settings, 'LOCAL_PADRAO_DOCUMENTOS', u'Teófilo Otoni, Minas Gerais')
    return render(request, 'frontend/rh/rh-controle-de-epi-imprimir.html', locals())
#
@user_passes_test(possui_perfil_acesso_rh)
def controle_de_epi_vincular_arquivo(request, controle_id):
    controle = get_object_or_404(ControleDeEquipamento, pk=controle_id)
    form_vincular = FormVincularArquivoControle(instance=controle)
    if request.POST:
        form_vincular = FormVincularArquivoControle(request.POST, request.FILES, instance=controle)
        if form_vincular.is_valid():
            controle = form_vincular.save(commit=False)
            controle.data_arquivo_impresso_assinado_recebido = datetime.date.today()
            controle.receptor_arquivo_impresso = request.user.funcionario
            controle.save()
            messages.success(request, "Arquivo de Controle de EPI #%s salvo com sucesso!" % controle.id)
            return redirect(reverse("rh:controle_de_epi"))
    return render(request, 'frontend/rh/rh-controle-de-epi-vincular-arquivo.html', locals())
#
@user_passes_test(possui_perfil_acesso_rh)
def controle_de_epi_retornar(request, controle_id, linha_id):
    linha = get_object_or_404(LinhaControleEquipamento, pk=linha_id, controle__id=controle_id)
    linha.data_devolvido = datetime.date.today()
    linha.funcionario_receptor = request.user.funcionario
    linha.save()
    messages.success(request, u"Sucesso! Linha de Equipamento de EPI #%s marcado como entregue." % linha.id)
    return redirect(reverse('rh:controle_de_epi') + "#retorno-equipamento-pendente")
#
# INDICADORES DO RH
#
# FORMS
class SelecionaAnoIndicadorRH(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(SelecionaAnoIndicadorRH, self).__init__(*args, **kwargs)
        # Opções deve ser:
        #(2012, 'Ano 2012: 20 Admissões, 5 Demissões')
        anos = PeriodoTrabalhado.objects.dates('inicio', 'year', order='DESC')
        anos_choice = [(str(a.year), str(a.year)) for a in anos]
        self.fields['ano'].choices = anos_choice
        self.fields['ano'].widget.attrs['class'] = 'input-small'

    ano = forms.ChoiceField()

# VIEWS
@user_passes_test(possui_perfil_acesso_rh)
def indicadores_do_rh(request):
    form_seleciona_ano = SelecionaAnoIndicadorRH(request.GET)
    resultado_admissao = []
    resultado_demissao = []
    resultado_ativos = []
    teste_ad = {}
    # cria dicionario com todos os ids de cargo vinculado por
    #cargo[2013] = (Nome Cargo, 1, 2, 3, 4, ... 12)
    try:
        ano = request.GET.get('ano', datetime.date.today().year)
        ano = int(ano)
    except:
        raise
        ano = datetime.date.today().year

    if ano:
        import calendar
        #
        # Relacionados a Cargo
        #
        admitidos_cargo = {}
        for departamento in Departamento.objects.all().order_by('-id'):
            admitidos_cargo[departamento] = {}
            for cargo in departamento.cargo_set.all():
                admitidos_cargo[departamento][cargo] = []
                linha_adm = []
                linha_adm.append(cargo.nome)
                #
                linha_dem = []
                linha_dem.append(cargo.nome)
                #
                linha_ativo = []
                linha_ativo.append(cargo.nome)
                # para cada mês
                for month in range(1,13):
                    mes = month
                    # admissão
                    admissoes_no_mes = PeriodoTrabalhado.objects.filter(inicio__year=ano, inicio__month=month, funcionario__cargo_inicial=cargo).count()
                    linha_adm.append(admissoes_no_mes)
                    # demissao
                    demissoes_no_mes = PeriodoTrabalhado.objects.filter(fim__year=ano, fim__month=month, funcionario__cargo_atual=cargo).count()
                    linha_dem.append(demissoes_no_mes)
                    # ativos
                    # ultimo dia no mes pesquisado
                    primeiro_dia = datetime.date(ano, mes, 1)
                    ultimo_dia = datetime.date(ano, mes, calendar.monthrange(ano,mes)[1])
                    # filtra todos os periodos trabalhados do ano
                    ativos_cargo_no_mes = AtribuicaoDeCargo.objects.filter(cargo=cargo)
                    ativos_no_mes = ativos_cargo_no_mes.filter(
                        Q(inicio__lte=primeiro_dia, fim=None) | \
                        Q(inicio__lte=primeiro_dia, fim__gt=ultimo_dia)
                    ).count()
                    linha_ativo.append(ativos_no_mes)
                resultado_admissao.append(linha_adm)
                resultado_demissao.append(linha_dem)
                resultado_ativos.append(linha_ativo)
                admitidos_cargo[departamento][cargo].append(linha_adm)
        admitidos_cargo = OrderedDict(sorted(admitidos_cargo.items()))
        #
        # Totalizadores
        #
        ## admissao
        total_admissao_mes = []
        total_admissao_mes.append("Total")
        for month in range(1,13):
            # admissão
            admissoes_no_mes = PeriodoTrabalhado.objects.filter(inicio__year=ano, inicio__month=month).count()
            total_admissao_mes.append(admissoes_no_mes)
        ## demissao
        total_demissao_mes = []
        total_demissao_mes.append("Total")
        for month in range(1,13):
            # demissao
            demissoes_no_mes = PeriodoTrabalhado.objects.filter(fim__year=ano, fim__month=month).count()
            total_demissao_mes.append(demissoes_no_mes)
        ## ativos
        total_ativos_mes = []
        total_ativos_mes.append("Total")
        for month in range(1,13):
            mes = month
            # ativos
            primeiro_dia = datetime.date(ano, mes, 1)
            ultimo_dia = datetime.date(ano, mes, calendar.monthrange(ano,mes)[1])
            ativos_no_mes = AtribuicaoDeCargo.objects.filter(
                Q(inicio__lte=primeiro_dia, fim=None) | \
                Q(inicio__lte=primeiro_dia, fim__gt=ultimo_dia)
            ).count()
            total_ativos_mes.append(ativos_no_mes)
        ## horas_extra
        horas_extra_mes = []
        horas_extra_mes.append("Total")
        for month in range(1,13):
            mes = month
            # ativos
            horas_extra_no_mes = AutorizacaoHoraExtra.objects.filter(
                data_execucao__month=mes, data_execucao__year=ano
            ).aggregate(Sum('quantidade'))['quantidade__sum'] or 0
            horas_extra_mes.append(horas_extra_no_mes)
        
        # retidos
        total_retidos_mes = []
        total_retidos_mes.append("Total")
        for month in range(1,13):
            mes = month
            # ativos
            primeiro_dia = datetime.date(ano, mes, 1)
            ultimo_dia = datetime.date(ano, mes, calendar.monthrange(ano,mes)[1])
            retidos = PeriodoTrabalhado.objects.filter(
                inicio__lte=primeiro_dia, fim=None
            ).count()
            total_retidos_mes.append(retidos)
        
        
        # por local de trabalho
        tabela_local_de_trabalho = {}
        for local in EnderecoEmpresa.objects.all():
            linha = []
            linha.append(local.nome)
            for month in range(1,13):
                mes = month
                primeiro_dia = datetime.date(ano, mes, 1)
                ultimo_dia = datetime.date(ano, mes, calendar.monthrange(ano,mes)[1])
                ativos_no_mes = AtribuicaoDeCargo.objects.filter(
                        local_empresa=local
                    ).filter(
                        Q(inicio__lte=primeiro_dia, fim=None) | \
                        Q(inicio__lte=primeiro_dia, fim__gt=ultimo_dia)
                    )
                linha.append(ativos_no_mes.count())
            tabela_local_de_trabalho[local.id] = linha
        # campo e escritorio
        tabela_campo_escritorio = {}
        for tipo in TIPO_DE_CARGO_CHOICES:
            linha = []
            linha.append(tipo[1])
            for month in range(1,13):
                mes = month
                primeiro_dia = datetime.date(ano, mes, 1)
                ultimo_dia = datetime.date(ano, mes, calendar.monthrange(ano,mes)[1])
                atribuicoes_cargo = AtribuicaoDeCargo.objects.filter(cargo__tipo=tipo[0])
                ativos_no_mes = atribuicoes_cargo.filter(
                    Q(inicio__lte=primeiro_dia, fim=None) | \
                    Q(inicio__lte=primeiro_dia, fim__gt=ultimo_dia)
                ).count()
                linha.append(ativos_no_mes)
            tabela_campo_escritorio[tipo[0]] = linha 
        
        # indicadores de promocao salarial
        total_promovidos_salario_mes=[]
        for month in range(1,13):
            mes = month
            # ativos
            promovidos = PromocaoSalario.objects.filter(
                data_promocao__month=mes, data_promocao__year=ano
            ).count()
            total_promovidos_salario_mes.append(promovidos)
        # indicadores de promocao cargo
        total_promovidos_cargo_mes=[]
        for month in range(1,13):
            mes = month
            # ativos
            promovidos = PromocaoCargo.objects.filter(
                data_promocao__month=mes, data_promocao__year=ano
            ).count()
            total_promovidos_cargo_mes.append(promovidos)
        
        
        # indicadores de treinamento de procedimento
        total_treinamento_procedimento_por_mes=[]
        total_treinamento_procedimento_por_mes_adicao=[]
        total_treinamento_procedimento_por_mes_atualizacao=[]
        for month in range(1,13):
            mes = month
            # ativos
            treinados = AtribuicaoDeResponsabilidade.objects.filter(
                data_treinado__month=mes, data_treinado__year=ano, treinamento_realizado=True
            ).aggregate(Sum('horas_treinadas'))['horas_treinadas__sum'] or 0
            treinados_adicao = AtribuicaoDeResponsabilidade.objects.filter(
                data_treinado__month=mes,
                data_treinado__year=ano,
                treinamento_realizado=True,
                tipo_de_treinamento='adicionar'
            ).aggregate(Sum('horas_treinadas'))['horas_treinadas__sum'] or 0
            treinados_atualizacao = AtribuicaoDeResponsabilidade.objects.filter(
                data_treinado__month=mes,
                data_treinado__year=ano,
                treinamento_realizado=True,
                tipo_de_treinamento='atualizar'
            ).aggregate(Sum('horas_treinadas'))['horas_treinadas__sum'] or 0
            total_treinamento_procedimento_por_mes.append(treinados)
            total_treinamento_procedimento_por_mes_adicao.append(treinados_adicao)
            total_treinamento_procedimento_por_mes_atualizacao.append(treinados_atualizacao)
        
        
        ## define ano como str
        ano = str(ano)
        # define que temos resultado
        resultados = True
        

    return render(request, 'frontend/rh/rh-indicadores.html', locals())


from django.views.decorators.csrf import csrf_exempt    
try:
    from django.utils import simplejson
except:
    import json as simplejson

@csrf_exempt
@login_required
def ajax_consulta_cargo(request):
    q = request.GET.get('q', None)
    mostra_preco = request.GET.get('mostra_preco', None)
    id_cargo = request.GET.get('id', None)
    if q:
        queries = q.split()
        qset1 =  reduce(operator.__and__, [Q(descricao__icontains=query) | Q(nome__icontains=query)  for query in queries])
        cargos = Cargo.objects.filter(qset1)
    if id_cargo:
        cargo = Cargo.objects.get(
            pk=id_cargo
        )
        if mostra_preco:
            nome_cargo = "%s - (R$ %s/h)" % (cargo.nome, cargo.fracao_hora_referencia)
        else:
            nome_cargo = "%s - %s" % cargo.nome
        result={"text":nome_cargo, "id": str(cargo.id), "preco": float(cargo.fracao_hora_referencia)}
        return HttpResponse(simplejson.dumps(result), content_type='application/json')
    result = []
    for cargo in cargos:
        if mostra_preco:
            nome_cargo = "%s - (R$ %s/h)" % (cargo.nome, cargo.fracao_hora_referencia)
        else:
            nome_cargo = "%s - %s" % cargo.nome
        
        result.append({"text":nome_cargo, "id": str(cargo.id), "preco": float(cargo.fracao_hora_referencia)})
    return HttpResponse(simplejson.dumps(result), content_type='application/json')