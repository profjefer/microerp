# -*- coding: utf-8 -*-
import datetime, os
from django.db import models, IntegrityError
from django.conf import settings
from django.db.models import signals

from django.core.exceptions import ValidationError

from django.db.models import Sum, Avg

import re
from django.template.defaultfilters import slugify


COMPONENTE_UNIDADE_MEDIDA = (
    ('und', 'Unidade'),
    ('m', 'Metro'),
)

FABRICANTE_FORNECEDOR_TIPO_CHOICES = (
    ('fabricante', 'Fabricante'),
    ('fornecedor', 'Fornecedor'),
)

STATUS_NOTA_FISCAL = (
    ('a', 'Aberta'),
    ('l', 'Lançada'),
)

TIPO_NOTA_FISCAL = (
    ('n', 'Nacional'),
    ('i', 'Internacional'),
)


TIPO_NACIONALIDADE_COMPONENTE = (
    ('n', 'Nacional'),
    ('i', 'Internacional'),
)


OPCAO_LINHA_SUBPRODUTO_PADRAO = (
    (True, 'Sim'),
    (False, u'Não'),
)

TIPO_DE_TESTES_SUBPRODUTO = (
    (0,  u'Nulo'),
    (1, "Simples"),
    (2, "Composto"),
)

ORDEM_DE_COMPRA_CRITICIDADE_CHOICES = (
    (0, 'Baixa'),
    (1, 'Média'),
    (2, 'Urgente'),
)

OPERACAO_MOVIMENTO_ESTOQUE_PRODUTO_CHOICES = (
    ('adiciona', 'Adiciona'),
    ('remove', 'Remove'),
)

SITUACAO_MOVIMENTO_ESTOQUE_SUBPRODUTO_CHOICES = (
    ('0', 'Montado'),
    ('1', 'Em Teste'),
    ('2', 'Funcional'),
)

TIPO_FALHA_DE_TESTE_CHOICES = (
    ('perda', 'Falha com Perda'),
    ('reparo', 'Falha com Reparo'),
)

class PerfilAcessoProducao(models.Model):
    '''Perfil de Acesso à Produção'''
    
    def __unicode__(self):
        if self.gerente:
            return u"Perfil de Acesso ao módulo Produção para %s do tipo Gerente" % self.user
        else:
            return u"Perfil de Acesso ao módulo Produção para %s do tipo Analista" % self.user
    
    class Meta:
        verbose_name = u"Perfil de Acesso à Produção"
        verbose_name_plural = u"Perfis de Acesso à Produção"
    
    gerente = models.BooleanField(default=False)
    gerente_de_compras = models.BooleanField(default=False)
    analista = models.BooleanField(default=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")

class EstoqueFisico(models.Model):
    
    def __unicode__(self):
        return u"%s (identificador: %s)" % (self.nome, self.identificacao)
    
    def posicao_componente(self, componente=None):
        if componente:
            try:
                ultima_posicao_componente = self.posicaoestoque_set.filter(componente=componente).order_by('-data_entrada')[0].quantidade
            except:
                ultima_posicao_componente = 0
            return ultima_posicao_componente
        else:
            return 0
    
    '''Estoque fisico onde se armazena componentes'''
    ativo = models.BooleanField(default=True)
    nome = models.CharField(blank=True, max_length=100)
    identificacao = models.SlugField(u"Abreviação", help_text=u"Abreviação para diretórios e urls")
    local_fisico = models.TextField(blank=True, null=True)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

class PosicaoEstoque(models.Model):
    '''Registro histórico de entradas de posicao de componentes em estoque fisico'''
    
    def __unicode__(self):
        return u"Posição do componente %s no dia %s no estoque %s" % (self.componente, self.data_entrada.strftime("%d/%m/%y %H:%M"), self.estoque)
    
    class Meta:
        ordering = ('-criado', '-id')
    
    data_entrada = models.DateTimeField(blank=True, default=datetime.datetime.now)
    nota_referencia = models.ForeignKey('NotaFiscal', blank=True, null=True, on_delete=models.PROTECT)
    ordem_producao_subproduto_referencia = models.ForeignKey('OrdemProducaoSubProduto', null=True, blank=True)
    ordem_producao_produto_referencia = models.ForeignKey('OrdemProducaoProduto', null=True, blank=True)
    ordem_producao_conversao_subproduto_referencia = models.ForeignKey('OrdemConversaoSubProduto', null=True, blank=True)
    componente = models.ForeignKey('Componente')
    estoque = models.ForeignKey('EstoqueFisico')
    quantidade = models.DecimalField(max_digits=15, decimal_places=2)
    quantidade_alterada = models.TextField(blank=True)
    # meta
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    justificativa = models.TextField(blank=True)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

class ComponenteTipo(models.Model):
    '''tipo/categoria de componente'''
    
    def save(self, *args, **kwargs):
            # se não existir part_number, forcar o padrao
            if not self.slug:
                self.slug = self.nome[0:3]
            super(ComponenteTipo, self).save(*args, **kwargs)    
    
    def clean(self):
        if self.slug == 'SUB' or self.slug == 'PRO':
            raise ValidationError(u"Erro! 'SUB' e 'PRO' são reservados para o sistema.")
    
    def __unicode__(self):
        return "%s - %s" % (self.slug, self.nome)
    
    slug = models.SlugField(u"Abreviação", max_length=3, unique=True, help_text=u"Abreviação para diretórios e urls")
    nome = models.CharField(u"Descrição", blank=False, null=False, max_length=100, unique=True)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

class LinhaFornecedorFabricanteComponente(models.Model):
    
    def __unicode__(self):
        return u"Linha de conversão em %s: %s <-> %s" % (self.fornecedor, self.part_number_fornecedor, self.componente)
    
    class Meta:
        unique_together = (('componente', 'part_number_fornecedor', 'fornecedor'))
        
    componente = models.ForeignKey('Componente')
    part_number_fornecedor = models.CharField(blank=True, max_length=100)
    fornecedor = models.ForeignKey('FabricanteFornecedor', related_name="fornecedor_componente_set")
    part_number_fabricante = models.CharField(blank=True, null=True, max_length=100, )
    fabricante = models.ForeignKey('FabricanteFornecedor', related_name="fabricante_componente_set", blank=True, null=True)


def componente_local_imagem(instance, filename):
    return os.path.join(
        'componente/', str(instance.part_number), 'imagem', filename
      )


class Componente(models.Model):
    '''Componente de SubProdutos e Produtos
    part_number deve ser formado por:
    self.tipo.nome[0:3]-self.identificador
    sendo este único
    '''
    
    def __unicode__(self):
        if self.part_number:
            return u"%s - %s" % (self.part_number, self.descricao)
        else:
            pn_prepend = getattr(settings, 'PN_PREPEND', 'PN')
            return u"%s-%s%s %s" % (pn_prepend, self.tipo.slug.upper(), "%04d" % self.identificador, self.descricao)
    
    def save(self, *args, **kwargs):
            pn_prepend = getattr(settings, 'PN_PREPEND', 'PN')
            # se não existir part_number, forcar o padrao
            if not self.part_number:
                self.part_number = u"%s-%s%s" % (pn_prepend, self.tipo.slug.upper(), "%04d" % self.identificador)
            super(Componente, self).save(*args, **kwargs)    
    
    def total_participacao_avulsa_produto(self):
        valor = 0
        linhas = self.linhacomponenteavulsodoproduto_set.all()
        for linha in linhas:
            if linha.quantidade:
                valor += linha.quantidade
        return valor
    
    def total_participacao_subproduto(self):
        valor = 0
        linhas = self.opcaolinhasubproduto_set.all()
        for linha in linhas:
            if linha.quantidade:
                valor += linha.quantidade
        return valor

    def total_participacao_padrao_subproduto(self):
        valor = 0
        linhas = self.opcaolinhasubproduto_set.filter(padrao=True)
        for linha in linhas:
            if linha.quantidade:
                valor += linha.quantidade
        return valor
        
    def total_participacao_alternativo_subproduto(self):
        valor = 0
        linhas = self.opcaolinhasubproduto_set.exclude(padrao=True)
        for linha in linhas:
            if linha.quantidade:
                valor += linha.quantidade
        return valor
    
    def total_unico_participacoes(self):
        return self.opcaolinhasubproduto_set.count() + self.linhacomponenteavulsodoproduto_set.count()
    
    def matriz_subproduto_participacao(self):
        matriz = []
        for subproduto in SubProduto.objects.filter(ativo=True):
            try:
                participacao_no_subproduto = subproduto.get_componentes()[self.pk]
            except:
                participacao_no_subproduto = None
            if participacao_no_subproduto:
                matriz.append((subproduto, participacao_no_subproduto))
        return matriz
    
    class Meta:
        unique_together = (('identificador', 'tipo'))
        ordering = ('part_number',)
    
    def posicao_no_estoque(self, estoque):
        try:
            posicao = self.posicaoestoque_set.filter(estoque=estoque).order_by('-data_entrada')[0].quantidade
        except:
            posicao = 0
        return posicao
    
    def posicao_no_estoque_produtor(self):
        slug_estoque_produtor = getattr(settings, 'ESTOQUE_FISICO_PRODUTOR', 'producao')
        estoque_produtor,created = EstoqueFisico.objects.get_or_create(identificacao=slug_estoque_produtor)
        return self.posicao_no_estoque(estoque_produtor) or 0
    
    def registrar_preco_medio(self):
        pm = LancamentoComponente.objects.filter(componente=self).aggregate(avg=Avg('valor_unitario_final'))['avg']
        self.preco_medio_unitario = pm
        self.save()
    
    def total_em_estoques(self):
        total_em_estoques = 0
        for estoque in EstoqueFisico.objects.all():
            total_em_estoques += self.posicao_no_estoque(estoque)
        return total_em_estoques
    
    
    def ultimo_part_number_fornecedor(self):
        if self.lancamentocomponente_set.all().last():
            return self.lancamentocomponente_set.all().last().part_number_fornecedor
        else:
            return None
    
    # geral
    ativo = models.BooleanField(default=True)
    imagem = models.ImageField(upload_to=componente_local_imagem, blank=True, null=True)
    part_number = models.CharField("PART NUMBER", help_text="IDENTIFICADOR GERADO AUTOMÁTICO", blank=True, null=True, max_length=100)
    identificador = models.IntegerField("Identificador único junto a categoria", blank=True, null=True, default=1)
    tipo = models.ForeignKey('ComponenteTipo', blank=False, null=False)    
    descricao = models.TextField("Descrição", blank=True)
    nacionalidade = models.CharField(blank=False, max_length=1, choices=TIPO_NACIONALIDADE_COMPONENTE)
    ncm = models.CharField("NCM", blank=True, max_length=100)
    # lead time
    lead_time = models.IntegerField("Lead Time (Semanas)", blank=False, null=False)
    
    ## preco_liquido_unitario_dolar
    #Obrigatorio se for componente importado, vai ser aramazenado o ultimo preco do T
    preco_liquido_unitario_dolar = models.DecimalField("Preço Líquido Unitário em Dólar", help_text="INSERIDO AUTOMATICAMENTE DA ULTIMA COMPRA", max_digits=10, decimal_places=2, default=0)
    
    # preco_bruto_unitrario_real - calculado no lancamento, onde deve ser preenchido a cotacao
    # do dolar, a incencia de imposto, vai ser calculado conforme a media dos lancamentos passados.
    preco_liquido_unitario_real = models.DecimalField("Preço Líquido Unitário em Real", help_text="INSERIDO AUTOMATICAMENTE DA ULTIMA COMPRA", max_digits=10, decimal_places=2, default=0)
    
    # preco_medio_unitario
    preco_medio_unitario = models.DecimalField("Preço Médio Bruto Unitário", max_digits=10, decimal_places=2, default=0)
    # medida
    medida = models.CharField(blank=True, max_length=100, choices=COMPONENTE_UNIDADE_MEDIDA, default='un')
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

def anexo_componente_local(instance, filename):
    return os.path.join(
        'componente/', str(instance.componente.part_number), 'anexos', filename
      )

class ArquivoAnexoComponente(models.Model):
    
    def __unicode__(self):
        return u"Arquivo %s anexo do Componente %s" % (self.arquivo, self.componente)
    
    componente = models.ForeignKey('Componente')
    arquivo = models.FileField(upload_to=anexo_componente_local)
    nome = models.CharField(blank=False, max_length=100)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")
    
    class Meta:
        ordering = ('criado',)

class FabricanteFornecedor(models.Model):
    
    def __unicode__(self):
        if self.tipo:
            return u"%s: %s" % (self.get_tipo_display(), self.nome)
        else:
            if self.nome:
                return self.nome
            else:
                return "Nome Não Preenchido"
    
    def nome_curto(self):
        return " ".join(self.nome.split()[0:2])
    
    
    class Meta:
        ordering = [('nome')]
    
    tipo = models.CharField(blank=True, max_length=100, choices=FABRICANTE_FORNECEDOR_TIPO_CHOICES)
    ativo = models.BooleanField(default=True)
    nome = models.CharField(u"Razão Social", blank=False, null=False, max_length=100)
    cnpj = models.CharField("CNPJ", blank=True, max_length=400)
    contatos = models.TextField(blank=True)
    rua = models.CharField(blank=True, max_length=100)
    numero = models.CharField(blank=True, max_length=100)
    bairro = models.CharField(blank=True, max_length=100)
    cep = models.CharField("CEP", blank=True, max_length=100)
    cidade = models.CharField(blank=True, max_length=100)
    estado = models.CharField(blank=True, max_length=100)
    telefone = models.CharField(blank=True, max_length=100)
    
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")


class LancamentoComponente(models.Model):
    
    def __unicode__(self):
        return u"Lançamento %s da nota %s Componente: %s" % (self.id, self.nota, self.componente)
        
    class Meta:
        unique_together = (('part_number_fornecedor', 'componente', 'nota'), ('part_number_fornecedor', 'nota'))
        ordering = ('peso', 'nota')
        
    def converter_part_number_fornecedor(self):
        '''Busca o part_number_fornecedor do produto na tabela de conversao e relaciona com o produto'''
        try:
            conversao = LinhaFornecedorFabricanteComponente.objects.get(part_number_fornecedor=self.part_number_fornecedor, fornecedor=self.nota.fabricante_fornecedor)
            self.componente = conversao.componente
            self.save()
        except:
            pass
            
    def calcula_totais_lancamento(self):
        if self.nota.status == 'a':
            if self.nota.tipo == 'n':
                # nota nacional, calculo direto, sem conversao, sem imposto
                self.valor_total_sem_imposto = float(self.quantidade) * float(self.valor_unitario)
                # nota nacional, calculo direto, sem conversao, com imposto
                percentual = float(self.valor_unitario) * float(self.impostos) / float(100)
                self.valor_total_com_imposto = (float(self.valor_unitario) + float(percentual)) * float(self.quantidade)
            elif self.nota.tipo == 'i':
                # nota internacional, calculo direto, com conversao de dolar, sem imposto
                self.valor_total_sem_imposto = float(self.quantidade) * float(self.valor_unitario) * float(self.nota.cotacao_dolar)
                # nota internacional, calculo direto, com conversao de dolar, com imposto
                percentual = float(self.valor_unitario * self.nota.cotacao_dolar) * float(self.impostos) / float(100)
                valor_unitario_em_real = float(self.valor_unitario * self.nota.cotacao_dolar)
                valor_unitario_em_real_com_imposto = float(valor_unitario_em_real) + float(percentual)
                self.valor_total_com_imposto = float(valor_unitario_em_real_com_imposto) * float(self.quantidade)
        self.save()
            
    #def save(self, *args, **kwargs):
            #self.calcula_totais_lancamento()            
            #super(LancamentoComponente, self).save(*args, **kwargs)
    
    def busca_part_number_na_memoria(self):
        # se tiver o part_number_fornecedor, buscar informações
        if self.part_number_fornecedor:
            conversoes = LinhaFornecedorFabricanteComponente.objects.filter(part_number_fornecedor=self.part_number_fornecedor, fornecedor=self.nota.fabricante_fornecedor)
            if conversoes.count() == 1:
                # so encontrou um, assumir como padrao
                self.fabricante = conversoes[0].fabricante
                self.part_number_fabricante = conversoes[0].part_number_fabricante
                self.componente = conversoes[0].componente
                self.save()
        
    def save(self, *args, **kwargs):
        super(LancamentoComponente, self).save(*args, **kwargs)
        #self.calcula_totais_lancamento()
        # mecanismo para atualizar a memoria de opcao do lancamento
        if self.aprender and self.part_number_fornecedor and self.componente:
            # aprender a combinacao de PN Fornecedor com PN Mestria, 
            # PN Fabricante e Fabricante para uso posterior
            conversao,created = LinhaFornecedorFabricanteComponente.objects.get_or_create(
                part_number_fornecedor=self.part_number_fornecedor,
                fornecedor=self.nota.fabricante_fornecedor,
                componente=self.componente
            )
            if created:
                conversao.componente = self.componente
                conversao.part_number_fornecedor = self.part_number_fornecedor
                conversao.part_number_fabricante = self.part_number_fabricante
                conversao.fabricante = self.fabricante
                conversao.save()
                # reinicia o valor do campo
            self.aprender = False
        

    def identificar_partnumber(self):
        # se tiver o part_number_fornecedor, buscar informações
        if self.part_number_fornecedor:
            conversoes = LinhaFornecedorFabricanteComponente.objects.filter(part_number_fornecedor=self.part_number_fornecedor, fornecedor=self.nota.fabricante_fornecedor)
            if conversoes.count() == 1:
                # so encontrou um, assumir como padrao
                self.fabricante = conversoes[0].fabricante
                self.part_number_fabricante = conversoes[0].part_number_fabricante
                self.componente = conversoes[0].componente
                self.save()
            #if conversoes.count() > 1:
            #    pns = []
            #    for l in conversoes:
            #        pns.append(l.componente)
            #    raise ValidationError(u'Erro! Este Part Number do Fornecedor aponta para mais de um PART NUMBER MESTRIA: %s' % pns)
            #if conversoes.count() == 0:
                # nenhuma conversao encontrada
            #    if self.componente:
                    # part number escolhido, checar se o partnumber já possui um código neste cliente
             #       try:
             #           conversao = LinhaFornecedorFabricanteComponente.objects.get(componente=self.componente, fornecedor=self.nota.fabricante_fornecedor)
            #            raise ValidationError(u'Erro! Este PART NUMBER MESTRIA já existe com o código de %s' % conversao.part_number_fornecedor)                        
            #        except LinhaFornecedorFabricanteComponente.DoesNotExist:
                        # nao possui, aprender se pedido for
            #            raise ValidationError(u'Aprender!')
                
            #    else:
            #        raise ValidationError(u'Erro! Part Number do Fornecedor não encontrado. Escolha o PART NUMBER MESTRIA')
            
                
    
    
    nota = models.ForeignKey('NotaFiscal')
    peso = models.IntegerField(blank=True, null=True)
    # quick create
    part_number_fornecedor = models.CharField("Part Number Fornecedor", blank=True, max_length=100)
    quantidade = models.DecimalField(max_digits=15, decimal_places=2)
    valor_unitario = models.DecimalField("Valor Unitário (R$)", max_digits=10, decimal_places=2, default=0)
    impostos = models.DecimalField("Incidência de Impostos (%)", help_text=u"Incidência total de impostos deste Lançamento em (%)", max_digits=10, decimal_places=2, default=0, blank=False, null=False)
    
    #campos automaticamente sugeridos, preenchidos opcionais
    componente = models.ForeignKey('Componente', verbose_name=getattr(settings, 'NOME_PART_NUMBER_INTERNO', 'PART NUMBER'), blank=True, null=True)
    fabricante = models.ForeignKey('FabricanteFornecedor', blank=True, null=True)
    part_number_fabricante = models.CharField("Part Number Fabricante", blank=True, max_length=100)
    
    # ativar o aprender / memorizar opcoes
    aprender = models.BooleanField(default=False)
    
    valor_total_sem_imposto = models.DecimalField("Total do Lançamento sem Imposto", help_text="Campo calculado automaticamente", max_digits=10, decimal_places=2, default=0, blank=False, null=False)
    valor_total_com_imposto = models.DecimalField("Total do Lançamento com Imposto", help_text="Campo calculado automaticamente", max_digits=10, decimal_places=2, default=0, blank=False, null=False)    
    valor_taxa_diversa_proporcional = models.DecimalField("Valor proporcional da Taxa Diversa da Nota", help_text="Campo calculado automaticamente", max_digits=10, decimal_places=2, default=0, blank=False, null=False)
    valor_unitario_final = models.DecimalField("Valor Unitário Bruto", help_text="Campo calculado automaticamente", max_digits=10, decimal_places=2, default=0, blank=False, null=False)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")
    
class NotaFiscal(models.Model):
    
    def __unicode__(self):
        return u"Nota Fiscal Série %s, Número: %s, %s de %s" % (self.numero_de_serie(), self.numero_identificador(), self.get_tipo_display(), self.fabricante_fornecedor)
    
    class Meta:
        unique_together = (('fabricante_fornecedor', 'numero'))
        ordering = ['-criado']
    
    def numero_de_serie(self):
        return self.serie
    
    def numero_identificador(self):
        return self.numero
    
    def lancar_no_estoque(self, user_id=None):
        '''lanca a nota fiscal no estoque configurado como receptor'''
        try:
            if self.status == 'a':
                # nota precisa estar aberta para ser lancada no estoque receptor
                slug_estoque_receptor = getattr(settings, 'ESTOQUE_FISICO_RECEPTOR', 'reserva')
                estoque_receptor,created = EstoqueFisico.objects.get_or_create(identificacao=slug_estoque_receptor)
                # para cada item da nota, lancar
                for item in self.lancamentocomponente_set.all():
                    try:
                        posicao_atual = PosicaoEstoque.objects.filter(estoque=estoque_receptor, componente=item.componente).order_by('-data_entrada')[0].quantidade
                    except:
                        posicao_atual = 0
                    posicao_calculada = posicao_atual + item.quantidade
                    posicao_nova = PosicaoEstoque.objects.create(estoque=estoque_receptor, componente=item.componente, quantidade=posicao_calculada, nota_referencia=self)
                    if user_id:
                        posicao_nova.criado_por_id = user_id
                        posicao_nova.save()
                    # registra o preco medio do compoente
                    item.componente.registrar_preco_medio()
                    if item.nota.tipo == 'i': # nota internacional
                        # registra o preco liquido unitario em dolar no componente, para memoria da proxima conta
                        item.componente.preco_liquido_unitario_dolar = item.valor_unitario
                        # converte de dolar pra real com a cotacao da nota
                        item.componente.preco_liquido_unitario_real = float(item.valor_unitario) * float(self.cotacao_dolar) 
                        # registra o preco liquido unitario em real
                    else:
                        item.componente.preco_liquido_unitario_real = item.valor_unitario
                    item.componente.save()
                        
                        

                self.status = 'l'
                self.save()
                return True
        except:
            raise
            return False
    
    def clean(self):
        if self.tipo == 'i' and not self.cotacao_dolar:
            raise ValidationError(u'Erro! Para Notas Fiscais Internacionais, é obrigatório preencher a cotação do dólar.')
        if self.status == 'l' and self.lancamentocomponente_set.count() == 0:
            raise ValidationError(u'Erro! Esta nota não possui nenhum lançamento!')    
    
    def calcula_totais_nota(self):
        if self.status == 'a':
            # calcula totais dos lancamentos
            # agrega totais dos lancamentos na nota
            totais = self.lancamentocomponente_set.aggregate(sem=Sum('valor_total_sem_imposto'),com=Sum('valor_total_com_imposto'))
            self.total_sem_imposto = totais['sem']
            self.total_com_imposto = totais['com']
            if self.tipo == 'i':
                if self.total_sem_imposto:
                    self.total_da_nota_em_dolar = self.total_sem_imposto / self.cotacao_dolar
                else:
                    self.total_da_nota_em_dolar = 0
            self.save()
            # distribui as taxas extra proporcionalmente
            for item in self.lancamentocomponente_set.all():
                # descobre qual a porcentagem do total do lancamento em relacao ao total da nota
                if self.total_com_imposto:
                    porcentagem = 100 * float(item.valor_total_com_imposto) / float(self.total_com_imposto)
                else:
                    porcentagem = 0
                # aplica o percentual encontrado às taxas extra
                # 100 - self.nota.taxas_diversas
                # percentual - x
                # x = percentual * taxas_diversas / 100
                valor_proporconal = porcentagem * float(self.taxas_diversas) / 100
                item.valor_taxa_diversa_proporcional = valor_proporconal
                # calcula valor unitario final:
                #   total do lancamento com impostos dividido por quantidade
                valor_unitario = float(item.valor_total_com_imposto) / float(item.quantidade)
                #   total do valor de taxas extra proporcial dividido por quantidade
                valor_taxas_extra_unitario = item.valor_taxa_diversa_proporcional / float(item.quantidade)
                # ambos somados, sao o numero final do valor unitario, para fins de calculo do preco medio
                item.valor_unitario_final = float(valor_taxas_extra_unitario) + float(valor_unitario)   
                item.save()
    
    #arquivo = models.FileField(upload_to=arquivo)
    numero = models.CharField("Número", max_length=100, blank=False, null=False)
    serie = models.CharField("Série / Tipo de Nota", max_length=100, blank=True, null=True)
    tipo = models.CharField(blank=False, max_length=1, choices=TIPO_NOTA_FISCAL)
    taxas_diversas = models.DecimalField("Valores Diversos (R$)", max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    cotacao_dolar = models.DecimalField("Cotação do Dolar em Relação ao Real (R$)", help_text="utilizado somente em notas Internacionais", max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(blank=True, max_length=100, choices=STATUS_NOTA_FISCAL, default='a')
    fabricante_fornecedor = models.ForeignKey('FabricanteFornecedor', verbose_name="Fornecedor")
    data_entrada = models.DateTimeField(blank=True, default=datetime.datetime.now)
    data_lancado_estoque = models.DateTimeField(blank=True, null=True)
    lancado_por = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    # totais e valores
    total_sem_imposto = models.DecimalField("Total da Nota sem Imposto", help_text="Campo calculado automaticamente", max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    total_com_imposto = models.DecimalField("Total da Nota com Imposto", help_text="Campo calculado automaticamente", max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    # para nota internacional
    total_da_nota_em_dolar = models.DecimalField("Total da Nota em Dolar", help_text="Campo calculado automaticamente", max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

# SUBPRODUTO

def subproduto_local_imagem(instance, filename):
    return os.path.join(
        'subproduto/', str(instance.slug), 'imagem', filename
      )

class SubProduto(models.Model):
    
    def __unicode__(self):
        pn_prepend = getattr(settings, 'PN_PREPEND', 'PN')
        return "%s %s - %s" % (self.part_number, self.nome, self.descricao)
    
    class Meta:
        verbose_name = "Sub Produto"
        ordering = ('part_number',)
    
    def subprodutos_agregados(self, lista=None, retorna_objeto=False):
        '''
        retorna uma lista com os ids ou objetos de todos os subprodutos abaixo, recursivamente
        '''
        if not lista:
            lista = []
        # para cada subproduto agregado
        for linha in self.linhasubprodutos_agregados.all().select_related():
            if retorna_objeto:
                lista.append(linha.subproduto_agregado)
            else:
                lista.append(int(linha.subproduto_agregado.id))
            lista = linha.subproduto_agregado.subprodutos_agregados(lista=lista, retorna_objeto=retorna_objeto)
        return lista
    
    def produzivel(self, quantidade=1):
        # descobre os componentes deste sub produto
        produzivel = True
        componentes = self.get_componentes()
        slug_estoque_produtor = getattr(settings, 'ESTOQUE_FISICO_PRODUTOR', 'producao')
        estoque_produtor,created = EstoqueFisico.objects.get_or_create(identificacao=slug_estoque_produtor)
        
        for item in componentes.items():
            if type(item[0]) == long:
                # componente, verificar estoque
                posicao_em_estoque_produtor = estoque_produtor.posicao_componente(item[0])
                valor_a_produzir = float(item[1]) * float(quantidade)
                if posicao_em_estoque_produtor < valor_a_produzir:
                    return False
            elif type(item[0]) == str:
                # subproduto
                id_subproduto = item[0].split('-')[1]
                subproduto = SubProduto.objects.values('total_funcional').get(id=id_subproduto)
                valor_a_produzir = float(item[1]) * float(quantidade)
                if subproduto['total_funcional'] < valor_a_produzir:
                    return False
        return True
            
    
    def get_componentes(self, dic=None, conf=None, multiplicador=1, agrega_subproduto_sem_teste=True):
        # componentes
        # se tiver configurado, calcular configurado
        if not dic:
            dic = {}
        if conf:
            # calcula a quantidade de componentes conforme a configuracao
            for k,v in conf.items():
                id_linha = k
                opcao = OpcaoLinhaSubProduto.objects.get(pk=v)
                try:
                    valor_atual = dic[opcao.componente.id]
                except:
                    valor_atual = 0
                # valor atual resgatado
                dic[opcao.componente.id] = float(valor_atual) + (float(opcao.quantidade) * float(multiplicador))
        # caso contrario,
        else:
            # monta dicionario com o padrao
            for linha in self.linhasubproduto_set.all():
                opcao_padrao = linha.opcao_padrao()
                if opcao_padrao:
                    componente = opcao_padrao.componente
                    quantidade_necessaria = float(opcao_padrao.quantidade)
                    # soma ao montante
                    try:
                        quantidade_atual = dic[opcao_padrao.componente.id]
                    except:
                        quantidade_atual = 0
                    dic[opcao_padrao.componente.id] = float(quantidade_atual) + (float(quantidade_necessaria) * float(multiplicador))

        
        # agora pro SUBPRODUTO
        # pega os subprodutos
        for linha_subproduto in self.linhasubprodutos_agregados.all():
            # para cada linha de subproduto
            # pega os componentes dele, somente se nao exigir testes
            if linha_subproduto.subproduto_agregado.tipo_de_teste and agrega_subproduto_sem_teste:
                try:
                    valor_atual = dic['subproduto-%s' % str(linha_subproduto.subproduto_agregado.id)]
                except:
                    valor_atual = 0
                dic['subproduto-%s' % str(linha_subproduto.subproduto_agregado.id)] = float(valor_atual) + (float(linha_subproduto.quantidade) * float(multiplicador))
                
            else:
                dic = linha_subproduto.subproduto_agregado.get_componentes(dic=dic, multiplicador=linha_subproduto.quantidade*multiplicador, agrega_subproduto_sem_teste=agrega_subproduto_sem_teste)
            # avanca sobre os subprodutos
        return dic
        
    
    def dicionario_quantidades_componentes_nos_subprodutos(self, dic=None, multiplicador=1):
        '''
            sempre recebe o dicionario de quantidades
            agrega os componentes do subproduto atual
            agrega todos os componentes dos subprodutos agregados
        '''
        if not dic:
            dic = {}
        # para cada linha de subproduto agregado, buscar quantidades
        for linha_agregados in self.linhasubprodutos_agregados.all():
            # pegar os componentes do agregado
            multiplicador = linha_agregados.quantidade * multiplicador
            dic = linha_agregados.subproduto_agregado.dicionario_quantidades_componentes(dic, multiplicador=linha_agregados.quantidade)
        return dic
    
    def dicionario_quantidades_componentes(self, dic=None, conf=None, multiplicador=1):
        '''
            recebe a configuracao da linha em dicionario
            calcula as quantidades de componentes
            retorna dicionario de componentesXquantidades
        '''
        if not dic:
            # primeira execucao
            dic = {}
        if conf:
            # calcula a quantidade de componentes conforme a configuracao
            for k,v in conf.items():
                id_linha = k
                opcao = OpcaoLinhaSubProduto.objects.get(pk=v)
                try:
                    valor_atual = dic[opcao.componente.id]
                except:
                    valor_atual = 0
                # valor atual resgatado
                dic[opcao.componente.id] = float(valor_atual) + (float(opcao.quantidade) * float(multiplicador))
        else:
            for linha in self.linhasubproduto_set.all():
                opcao_padrao = linha.opcao_padrao()
                componente = opcao_padrao.componente
                quantidade_necessaria = float(opcao_padrao.quantidade)
                # soma ao montante
                try:
                    quantidade_atual = dic[opcao_padrao.componente.id]
                except:
                    quantidade_atual = 0
                dic[opcao_padrao.componente.id] = float(quantidade_atual) + (float(quantidade_necessaria) * float(multiplicador))
        return dic            
    
    def total_participacao(self):
        # verifica se este produto esta agregado em outro subproduto
        agregado_em_subproduto = LinhaSubProdutoAgregado.objects.filter(subproduto_agregado=self).count()    
        agregado_em_produto = LinhaSubProdutodoProduto.objects.filter(subproduto=self).count()
        return agregado_em_subproduto + agregado_em_produto
    
    def dicionario_quantidades_utilizadas_padrao(self, dic=None, fator_multiplicador=1):
        '''retorna um dicionario de todos os componentes utilizados por padrão'''
        if not dic:
            dic_componentes={}
        else:
            dic_componentes = dic
        #primeiro, considerar os componentes
        for linha in self.linhasubproduto_set.all():
            opcao_padrao = linha.opcao_padrao()
            if opcao_padrao:
                componente = opcao_padrao.componente
                quantidade_necessaria = float(opcao_padrao.quantidade)
                # soma ao montante
                try:
                    quantidade_atual = dic_componentes[str(opcao_padrao.componente.id)]
                except:
                    quantidade_atual = 0
                dic_componentes[str(opcao_padrao.componente.id)] = float(quantidade_atual) + (float(quantidade_necessaria) * float(fator_multiplicador))

        #segundo, considerar subprodutos
        for linha in self.linhasubprodutos_agregados.all():
            dic_componentes = linha.subproduto_agregado.dicionario_quantidades_utilizadas_padrao(dic_componentes, fator_multiplicador=linha.quantidade)
        return dic_componentes

    def save(self, *args, **kwargs):
        """Auto-populate an empty slug field from the MyModel name and
        if it conflicts with an existing slug then append a number and try
        saving again.
        """

        if not self.part_number:
            super(SubProduto, self).save()
            pn_prepend = getattr(settings, 'PN_PREPEND', 'PN')
            self.part_number = "%s-SUB%s" % (pn_prepend, "%04d" % self.id,)

        if not self.slug:
            self.slug = slugify(self.nome)

        while True:
            try:
                super(SubProduto, self).save()
            # Assuming the IntegrityError is due to a slug fight
            except IntegrityError:
                match_obj = re.match(r'^(.*)-(\d+)$', self.slug)
                if match_obj:
                    next_int = int(match_obj.group(2)) + 1
                    self.slug = match_obj.group(1) + '-' + str(next_int)
                else:
                    self.slug += '-2'
            else:
                break
    
    def custo_total_linhas2(self):
        '''calcula o custo total deste subproduto, incluindo as quantidades de linha'''
        memoria_calculo_linha = OpcaoLinhaSubProduto.objects.filter(padrao=True, linha__subproduto=self).values('componente__preco_medio_unitario', 'quantidade')
        retorno = 0
        for item in memoria_calculo_linha:
            retorno += item['quantidade'] * item['componente__preco_medio_unitario']
        return retorno
        
    def custo_total_linhas(self):
        '''calcula o custo total deste subproduto, incluindo as quantidades de linha'''
        # total de linhas
        return self.custo_total_linhas2()
    
    def custo_total_dos_sub_produtos_agregados(self):
        total_parcial = 0
        for linha in self.linhasubprodutos_agregados.all():
            total_parcial += linha.quantidade * linha.subproduto_agregado.custo()
        return total_parcial
    
    def custo(self):
        return self.custo_total_linhas() + self.custo_total_dos_sub_produtos_agregados()
    
    def custo_dolar_componentes_internacionais2(self):
        memoria_calculo_linha = OpcaoLinhaSubProduto.objects.filter(padrao=True, linha__subproduto=self, componente__nacionalidade='i').values('componente__preco_medio_unitario', 'componente__part_number', 'quantidade')
        retorno = 0
        for item in memoria_calculo_linha:
            retorno += item['quantidade'] * item['componente__preco_medio_unitario']
        return retorno
    
    def custo_dolar_componentes_internacionais(self):
        '''calcula o custo total deste subproduto, somente dos componentes internacionais'''
        return self.custo_dolar_componentes_internacionais2()
        # total de linhas
        total_parcial = 0
        # para cada linha
        for linha in self.linhasubproduto_set.all():
            # somente as linhas que possuem opcao padrao
            padrao = linha.opcao_padrao()
            if padrao and padrao.quantidade and padrao.componente.preco_liquido_unitario_real:
                if padrao.componente.nacionalidade == 'i':
                    valor = padrao.quantidade * padrao.componente.preco_liquido_unitario_dolar
                    total_parcial += valor
        return total_parcial        
    
    def maximo_produzivel_agrupado(self, agrega_subproduto_sem_teste=True):
        return self.maximo_produzivel(agrega_subproduto_sem_teste=agrega_subproduto_sem_teste)
    
    def maximo_produzivel(self, agrega_subproduto_sem_teste=False):
        modulos = []
        # pega todos os componentes, sem agregar subprodutos sem teste
        componentes = self.get_componentes(agrega_subproduto_sem_teste=agrega_subproduto_sem_teste)
        slug_estoque_produtor = getattr(settings, 'ESTOQUE_FISICO_PRODUTOR', 'producao')
        estoque_produtor,created = EstoqueFisico.objects.get_or_create(identificacao=slug_estoque_produtor)
        for item in componentes.items():
            if type(item[0]) == long:
                posicao_em_estoque_produtor = estoque_produtor.posicao_componente(item[0])
                print "Item Componente: %s" % item[0]
                print "Posicao em estoque: %s" % posicao_em_estoque_produtor
                print "Quantidade necessaria de producao: %s" % item[1]
                if item[1] != 0:
                    diferenca = float(posicao_em_estoque_produtor) / float(item[1])
                else:
                    diferenca = 0
                print "Diferença: %s" % diferenca
                print "####"*10
                modulos.append(diferenca)
            elif type(item[0]) == str:
                # subproduto
                id_subproduto = item[0].split('-')[1]
                subproduto = SubProduto.objects.values('total_funcional').get(id=id_subproduto)
                diferenca = float(subproduto['total_funcional']) / float(item[1])
                print "Item SubProduto: %s" % item[0]
                print "Quantidade Funcional: %s" % subproduto['total_funcional']
                print "Quantidade necessaria de producao: %s" % item[1]
                print "Diferença: %s" % diferenca
                print "####"*10
                modulos.append(diferenca)
        
        if modulos:
            print modulos
            x = min(float(s) for s in modulos)
            return int(x)
        else:
            return 0
        
    
    def total_disponivel(self):
        # subproduto com tipo de teste nulo, ou seja
        # total disponível é direto no estoque
        slug_estoque_produtor = getattr(settings, 'ESTOQUE_FISICO_PRODUTOR', 'producao')
        estoque_produtor,created = EstoqueFisico.objects.get_or_create(identificacao=slug_estoque_produtor)
        if not self.tipo_de_teste:
            # este valor deverá ser calculado automaticamente,
            # pois o produto não precisa de teste e pode ser criado na hora
            # retornar a maior quantidade possível que
            # pode ser produzido deste SubProduto            
            componentes = self.get_componentes()
            modulos = []
            
            for item in componentes.items():
                if type(item[0]) == long:
                    posicao_em_estoque_produtor = estoque_produtor.posicao_componente(item[0])
                    if item[1]:
                        diferenca = float(posicao_em_estoque_produtor) / float(item[1])
                    else:
                        diferenca = 0
                    modulos.append(diferenca)
                elif type(item[0]) == str:
                    # subproduto
                    id_subproduto = item[0].split('-')[1]
                    subproduto = SubProduto.objects.values('total_funcional').get(id=id_subproduto)
                    diferenca = float(subproduto['total_funcional']) / float(item[1])
                    modulos.append(diferenca)
            
            if modulos:
                x = min(float(s) for s in modulos)
                return int(x)
            else:
                return 0
                    
        # subproduto com teste, deve ser produzido, testado,
        # e depois armazenado em total_funcional
        else:
            return self.total_funcional

    ativo = models.BooleanField(default=True)
    imagem = models.ImageField(upload_to=subproduto_local_imagem, blank=True, null=True)
    nome = models.CharField(blank=False, max_length=100)
    slug = models.SlugField(u"Abreviação", blank=True, null=True, unique=True, help_text=u"Abreviação para diretórios e urls")
    part_number = models.CharField(blank=True, max_length=100)
    descricao = models.TextField(u"Descrição", blank=True)
    possui_tags = models.BooleanField(default=True, help_text="Se este campo for marcado, as Linhas do Sub Produto deverão ser alocadas para uma TAG única.")
    tipo_de_teste = models.IntegerField(blank=False, null=False, default=0, choices=TIPO_DE_TESTES_SUBPRODUTO)
    # totalizadores de teste
    total_montado = models.IntegerField(blank=False, null=False, default=0)
    total_testando = models.IntegerField(blank=False, null=False, default=0)
    total_funcional = models.IntegerField(blank=False, null=False, default=0)
    # valor total
    valor_total_de_custo = models.DecimalField(max_digits=10, decimal_places=2)
    valor_custo_total_linhas =  models.DecimalField(max_digits=10, decimal_places=2)
    valor_custo_total_dos_sub_produtos_agregados =  models.DecimalField(max_digits=10, decimal_places=2)
    # notacao de producao
    notacao_de_producao = models.TextField(blank=True, default="{}")
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")
    
class LinhaSubProdutoAgregado(models.Model):
    ''' linha com os subprodutos e suas quantidades agregadas'''
    
    def __unicode__(self):
        return "%s Unidades do SubProduto %s Agregado ao %s" % (self.quantidade, self.subproduto_agregado.part_number, self.subproduto_principal.part_number)
    
    
    def linha_produzivel(self):
        return self.subproduto_agregado.produzivel(quantidade=self.quantidade)
    
    class Meta:
        verbose_name = "Linha Sub Produto Agregado"
        verbose_name_plural = "Linha de Sub Produtos Agregados"
    
    def clean(self):
        if self.quantidade == 0:
            raise ValidationError(u"Erro! Quantidade deve ser maior que 0")
    
    def custo(self):
        return self.quantidade * self.subproduto_agregado.custo()
        
    
    def disponivel_estoque(self):
        if self.quantidade > self.subproduto_agregado.total_funcional:
            return True
        else:
            return False
    
    def ipp(self):
        '''Índice de Peso de Participacao'''
        total = self.subproduto_principal.custo()
        ipp = 100 * self.custo() / total
        return ipp
    
    quantidade = models.IntegerField(help_text=u"Número Inteiro", blank=True, null=True, default=1)
    subproduto_principal = models.ForeignKey('SubProduto', related_name="linhasubprodutos_agregados")
    subproduto_agregado = models.ForeignKey('SubProduto', related_name="linhasubprodutos_escolhidos")

class LinhaSubProduto(models.Model):
    '''
    Modelo de Objeto
    '''
    
    def opcao_padrao(self):
        try:
            padrao = self.opcaolinhasubproduto_set.get(padrao=True)
            return padrao
        except:
            return None
    
    def __unicode__(self):
        return u"Linha %s de SubProduto %s" % (self.id, self.subproduto)
    
    class Meta:
        verbose_name = "Linha de Componentes do Sub Produto"
        verbose_name_plural = "Linhas de Componentes do Sub Produto"
        ordering = 'tag',
    
    def clean(self, exclude=None):
        if self.subproduto.possui_tags:
            # subproduto tagueavel
            linha_igual = LinhaSubProduto.objects.filter(tag=self.tag, subproduto=self.subproduto)
            if linha_igual and linha_igual [0] != self:
                raise ValidationError('Erro! Já existe uma Linha de Sub Produto com essa TAG!')

    def custo(self):
        padrao = self.opcao_padrao()
        if padrao and padrao.quantidade and padrao.componente.preco_medio_unitario:
            valor = padrao.quantidade * padrao.componente.preco_medio_unitario
            return valor or 0
        else:
            return 0

    def ipp(self):
        '''Índice de Peso de Participacao'''
        total = self.subproduto.custo()
        if total == 0:
            return 0
        else:
            ipp = 100 * self.custo() / total
            return ipp

    peso = models.IntegerField("Item", blank=True, null=True)
    subproduto = models.ForeignKey('SubProduto')
    tag = models.CharField("TAG", blank=True, max_length=100)
    valor_custo_da_linha = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

class OpcaoLinhaSubProduto(models.Model):

    def __unicode__(self):
        if self.padrao:
            padrao = u"(Padrão)"
        else:
            padrao = ''
        return "%s %s de %s %s" % (self.quantidade, self.componente.medida, self.componente, padrao)

    class Meta:
        verbose_name = u"Opção para a Linha do SubProduto"
        unique_together = (('linha', 'padrao'))
        ordering = '-padrao',
    
    def custo(self):
        valor = 0
        valor = float(self.quantidade) * float(self.componente.preco_medio_unitario)
        return valor
        
    linha = models.ForeignKey('LinhaSubProduto')
    componente = models.ForeignKey('Componente')
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    padrao = models.NullBooleanField(u"Padrão", default=False)
    
def subproduto_local_documentos(instance, filename):
    return os.path.join(
        'subproduto/', str(instance.subproduto.slug), 'documento', filename
      )

class DocumentoTecnicoSubProduto(models.Model):
    
    def __unicode__(self):
        return u"Documento Técnico %s do SubProduto %s" % (self.arquivo, self.subproduto)
    
    class Meta:
        verbose_name = u"Documento Técnico do Sub Produto"
        verbose_name_plural = u"Documentos Técnicos do Sub Produto"
    
    subproduto = models.ForeignKey('SubProduto')
    nome = models.CharField(blank=False, max_length=100)
    arquivo = models.FileField(upload_to=subproduto_local_documentos, blank=False, null=False)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")
    

class ProdutoFinal(models.Model):
    
    def __unicode__(self):
        pn_prepend = getattr(settings, 'PN_PREPEND', 'PN')
        return u"%s-PRO%s %s - %s" % (pn_prepend, "%04d" % self.id, self.nome, self.descricao)

    class Meta:
        ordering = ('part_number',)

    def subprodutos_agregados(self, lista=None, retorna_objeto=False):
        '''
        retorna uma lista com os ids ou objetos de todos os subprodutos abaixo, recursivamente
        '''
        if not lista:
            lista = []
        # para cada subproduto agregado
        for linha in self.linhasubprodutodoproduto_set.all().select_related():
            if retorna_objeto:
                lista.append(linha.subproduto)
            else:
                lista.append(int(linha.subproduto.id))
            lista = linha.subproduto.subprodutos_agregados(lista=lista, retorna_objeto=retorna_objeto)
        return lista


    def custo_total_linha_subprodutos(self):
        valor = 0
        for linha in self.linhasubprodutodoproduto_set.all():
            if linha.quantidade:
                valor += linha.custo()
        return valor

    def custo_total_linha_produtos_avulsos(self):
        valor = 0
        for linha in self.linhacomponenteavulsodoproduto_set.all():
            if linha.quantidade:
                valor += linha.custo()
        return valor

    def custo(self):
        return self.custo_total_linha_subprodutos() + self.custo_total_linha_produtos_avulsos()

    def get_componentes_produto(self, dic=None, multiplicador=1, agrega_subproduto_sem_teste=True):
        if not dic:
            dic = {}
        # contabiliza os componentes do próprio produto
        for linha in self.linhacomponenteavulsodoproduto_set.all():
            componente = linha.componente
            quantidade_necessaria = float(linha.quantidade)
            # soma ao montante
            try:
                quantidade_atual = dic[linha.componente.id]
            except:
                quantidade_atual = 0
            dic[linha.componente.id] = float(quantidade_atual) + (float(quantidade_necessaria) * float(multiplicador))

        # contabiliza os componentes de cada subproduto
        for linha in self.linhasubprodutodoproduto_set.all():
            # tipo de teste existe
            # somente incrementar a quantidade
            if linha.subproduto.tipo_de_teste and agrega_subproduto_sem_teste:
                try:
                    valor_atual = dic['subproduto-%s' % str(linha.subproduto.id)]
                except:
                    valor_atual = 0
                dic['subproduto-%s' % str(linha.subproduto.id)] = float(valor_atual) + (float(linha.quantidade) * float(multiplicador))
            else:
                # nao existe teste, pegar direto os componentes ou subprodutos na mesma situacao
                dic = linha.subproduto.get_componentes(dic=dic, multiplicador=float(linha.quantidade) * float(multiplicador), agrega_subproduto_sem_teste=agrega_subproduto_sem_teste)
            
        return dic

    def custo_internacional(self):
        valor = 0
        for linha in self.linhasubprodutodoproduto_set.all():
            if linha.quantidade:
                valor += linha.quantidade * linha.subproduto.custo_dolar_componentes_internacionais()
        for linha in self.linhacomponenteavulsodoproduto_set.filter(componente__nacionalidade='i').all():
            if linha.quantidade:
                valor += linha.quantidade * linha.componente.preco_liquido_unitario_dolar
        return valor

        

    def save(self):
        """Auto-populate an empty slug field from the MyModel name and
        if it conflicts with an existing slug then append a number and try
        saving again.
        """
        if not self.slug:
            self.slug = slugify(self.nome)
        
        if not self.part_number:
            super(ProdutoFinal, self).save()
            pn_prepend = getattr(settings, 'PN_PREPEND', 'PN')
            self.part_number = "%s-PRO%s" % (pn_prepend, "%04d" % self.id,)

        while True:
            try:
                super(ProdutoFinal, self).save()
            # Assuming the IntegrityError is due to a slug fight
            except IntegrityError:
                match_obj = re.match(r'^(.*)-(\d+)$', self.slug)
                if match_obj:
                    next_int = int(match_obj.group(2)) + 1
                    self.slug = match_obj.group(1) + '-' + str(next_int)
                else:
                    self.slug += '-2'
            else:
                break

    def lancamentos_disponiveis(self):
        return self.lancamentoprodproduto_set.filter(produto=self, vendido=False, apagado=False)
    
    def lancamentos_disponiveis_venda(self):
        return self.lancamentoprodproduto_set.filter(produto=self, vendido=False, apagado=False).exclude(serial_number=None)
    

    ativo = models.BooleanField(default=True)
    imagem = models.ImageField(upload_to=subproduto_local_imagem, blank=True, null=True)
    nome = models.CharField(blank=False, max_length=100)
    slug = models.SlugField(u"Abreviação", blank=True, null=True, unique=True, help_text=u"Abreviação para diretórios e urls")
    part_number = models.CharField(blank=True, max_length=100)
    descricao = models.TextField(u"Descrição", blank=True)
    total_produzido = models.IntegerField(blank=False, null=False, default=0)
    quantidade_estimada_producao_semanal = models.IntegerField(u"Quantidade Estimada de Produção Semanal", blank=False, null=False)
    quantidade_maxima_estocavel = models.IntegerField(u"Quantidade Máxima de Produto Estocável", blank=False, null=True)
    subprodutos_testaveis = models.ManyToManyField('SubProduto', blank=True, null=True)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")
    
class LinhaSubProdutodoProduto(models.Model):    
    
    class Meta:
        verbose_name = "Linha de Sub Produto do Produto"
        verbose_name_plural = "Linhas Sub Produto do Produto"
        ordering = ('-criado', '-id')
        unique_together = (('produto', 'subproduto'),)
    
    def custo(self):
        return self.subproduto.custo() * self.quantidade
    
    def clean(self):
        if self.quantidade == 0:
            raise ValidationError(u'Quantidade não pode ser 0')
    
    def ipp(self):
        '''Índice de Peso de Participacao'''
        total = self.produto.custo()
        ipp = 100 * self.custo() / total
        return ipp
    
    produto = models.ForeignKey('ProdutoFinal')
    quantidade = models.IntegerField(blank=False, null=False, default=1)
    subproduto = models.ForeignKey('SubProduto')
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")
    

class LinhaComponenteAvulsodoProduto(models.Model):
    
    def __unicode__(self):
        return u"Participação de %s Unidades Avulsas do Componente %s no Produto %s" % (self.quantidade, self.componente, self.produto)
    
    def custo(self):
        valor = 0
        if self.quantidade:
            valor = self.quantidade * self.componente.preco_medio_unitario
        return valor
    
    def clean(self):
        if self.quantidade == 0:
            raise ValidationError(u"Erro! Quantidade deve ser maior que 0")
    
    def ipp(self):
        '''Índice de Peso de Participacao'''
        total = self.produto.custo()
        ipp = 100 * self.custo() / total
        return ipp
    
    class Meta:
        verbose_name = "Linha de Componente Avulso do Produto"
        verbose_name_plural = "Linhas de Componentes Avulsos do Produto"
    
    produto = models.ForeignKey('ProdutoFinal')
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    componente = models.ForeignKey('Componente')
    
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")
    

def produto_local_documentos(instance, filename):
    return os.path.join(
        'produto/', str(instance.produto.slug), 'documento', filename
      )

class DocumentoTecnicoProduto(models.Model):
    
    def __unicode__(self):
        return u"Documento Técnico %s do Produto %s" % (self.arquivo, self.produto)
    
    
    class Meta:
        verbose_name = u"Documento Técnico do Sub Produto"
        verbose_name_plural = u"Documentos Técnicos do Sub Produto"
    
    produto = models.ForeignKey('ProdutoFinal')
    arquivo = models.FileField(upload_to=produto_local_documentos)
    nome = models.CharField(blank=False, max_length=100)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

class OrdemProducaoSubProduto(models.Model):
    
    def __unicode__(self):
        return u"Ordem de Produção #%s de %s unidades do Sub Produto %s" % (self.id, self.quantidade, self.subproduto)
    
    class Meta:
        verbose_name = u"Ordem de Produção do Sub Produto"
        verbose_name_plural = u"Ordens de Produção do Sub Produto"
        ordering = ['-criado']
    
    subproduto = models.ForeignKey('SubProduto')
    quantidade = models.IntegerField(blank=False, null=False)
    string_producao = models.TextField(blank=False)
    funcionario_produtor = models.ForeignKey('rh.Funcionario', verbose_name=u"Funcionário Produtor")
    data_producao = models.DateField(default=datetime.datetime.today)
    # meta
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

class OrdemConversaoSubProduto(models.Model):
    subproduto_original = models.ForeignKey('SubProduto', related_name="ordem_conversao_subproduto_original_set")
    subproduto_destino = models.ForeignKey('SubProduto', related_name="ordem_conversao_subproduto_destino_set")
    quantidade = models.IntegerField(blank=False, null=False)
    string_producao = models.TextField(blank=False)
    # meta
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

## PRODUCAO PRODUTO
class OrdemProducaoProduto(models.Model):
    
    class Meta:
        ordering = ['-criado']
    
    def __unicode__(self):
        return u"Ordem de Produção #%s de %s Produtos %s por %s em %s " \
            % (self.id, self.quantidade, self.produto.part_number, self.criado_por, self.criado.strftime("%d/%m/%y %H:%M"))
    
    produto = models.ForeignKey('ProdutoFinal')
    quantidade = models.IntegerField(blank=False, null=False)
    string_producao = models.TextField(blank=False)
    # meta
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

class LancamentoProdProduto(models.Model):
    
    def __unicode__(self):
        if self.serial_number:
            if self.vendido:
                texto = u"Produto %s com Serial: %s, vendido para %s" % \
                    (self.produto.part_number, self.serial_number, self.cliente_associado)
            else:
                texto = u"Produto %s com Serial: %s, Disponível" % \
                    (self.produto.part_number, self.serial_number)
        else:
            texto = u"Produto %s sem Serial. Disponível" % \
                self.produto.part_number
        if self.apagado:
            texto = "%s - APAGADO" % texto
        return texto        
    
    class Meta:
        verbose_name = u"Lançamento de Produção de Produto"
        verbose_name_plural = u"Lançamentos de Produção de Produto"
        ordering = ['-criado']
    
    def produto(self):
        return self.ordem_de_producao.produto
    
    serial_number = models.CharField(null=True, blank=False, max_length=100, default=None)
    funcionario_que_montou = models.ForeignKey('rh.Funcionario', blank=True, null=True, related_name="lancamento_de_producao_produto_montado_set", verbose_name=u"Funcionário que montou")
    data_montagem = models.DateField("Data de Montagem", blank=True, null=True, default=datetime.datetime.today)
    funcionario_inicio_teste = models.ForeignKey('rh.Funcionario', related_name="lancamento_de_producao_produto_teste_iniciado_set", blank=True, null=True, verbose_name=u"Funcionário que iniciou o teste"  )
    inicio_teste = models.DateField(blank=True, null=True,  default=datetime.datetime.today, verbose_name="Início de Teste")
    funcionario_relalizou_teste = models.ForeignKey('rh.Funcionario', related_name="lancamento_de_producao_produto_teste_realizado_set", blank=True, null=True, verbose_name=u"Funcionário que realizou o teste"  )
    realizacao_procedimento_de_teste = models.DateField(blank=True, null=True,  default=datetime.datetime.today, verbose_name=u"Realização de Procedimento de Teste")
    funcionario_finalizou_teste = models.ForeignKey('rh.Funcionario', related_name="lancamento_de_producao_produto_teste_finalizado_set", blank=True, null=True, verbose_name=u"Funcionário que finalizou o teste"  )
    fim_teste = models.DateField(blank=True, null=True,  default=datetime.datetime.today, verbose_name="Fim de Teste")
    cliente_associado = models.CharField(blank=True, null=True,  max_length=100)
    ordem_de_producao = models.ForeignKey(OrdemProducaoProduto, blank=True, null=True)
    observacoes = models.TextField(u"Observações", blank=True)
    produto = models.ForeignKey(ProdutoFinal)
    nota_fiscal = models.ForeignKey('NotaFiscalLancamentosProducao', blank=True, null=True)
    # meta
    ## adicao
    adicionado_manualmente = models.BooleanField(default=True)
    justificativa_adicionado = models.TextField(blank=True)
    funcionario_adicionou = models.ForeignKey('rh.Funcionario', related_name="lancamento_de_producao_produto_adicionado_set", blank=True, null=True)
    # remocao
    apagado = models.BooleanField(default=False)
    justificativa_apagado = models.TextField(blank=True)
    funcionario_apagou = models.ForeignKey('rh.Funcionario', related_name="lancamento_de_producao_produto_apagado_set", blank=True, null=True)
    data_apagado = models.DateTimeField(default=None, blank=True, null=True)
    # venda
    vendido = models.BooleanField(default=False)
    data_vendido = models.DateTimeField(default=None, blank=True, null=True)
    funcionario_vendeu = models.ForeignKey('rh.Funcionario', related_name="lancamento_de_producao_produto_vendido_set", blank=True, null=True)    
    # outros
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

class LinhaTesteLancamentoProdProduto(models.Model):
    
    class Meta:
        verbose_name = u"Teste de Lançamento de Produto Produzido"
        verbose_name_plural = u"Testes do Lançamento de Produto Produzido"
        ordering = ['-criado']
    
    lancamento_de_producao = models.ForeignKey(LancamentoProdProduto, verbose_name=u"Lançamento de Produção do Produto")
    subproduto_testavel = models.ForeignKey(SubProduto, verbose_name=u'Sub Produto Testável')
    funcionario_que_testou = models.ForeignKey('rh.Funcionario', related_name="linha_de_teste_de_lancamento_de_produto_set", null=True, blank=True)
    funcionario_que_montou = models.ForeignKey('rh.Funcionario', related_name="linha_de_montagem_de_lancamento_de_produto_set", null=True, blank=True)
    versao_firmware = models.CharField(u"Versão do Firmware", blank=True, max_length=100)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

class RegistroEnvioDeTesteSubProduto(models.Model):
    
    class Meta:
        verbose_name = u"Registro de Envio de Testes do Sub Produto"
        verbose_name_plural = u"Registros de Envio de Testes do Sub Produto"
        ordering = ['-criado']
    
    quantidade = models.IntegerField(blank=False, null=False)
    subproduto = models.ForeignKey('SubProduto')
    funcionario = models.ForeignKey('rh.Funcionario')
    data_envio = models.DateTimeField(blank=False, default=datetime.datetime.now)
    # meta
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

class RegistroSaidaDeTesteSubProduto(models.Model):
    
    class Meta:
        verbose_name = u"Registro de Saída de Testes do Sub Produto"
        verbose_name_plural = u"Registros de Saída de Testes do Sub Produto"
        ordering = ['-criado']
    
    quantidade = models.IntegerField(blank=False, null=False)
    subproduto = models.ForeignKey('SubProduto')
    funcionario = models.ForeignKey('rh.Funcionario')
    data_envio = models.DateTimeField(blank=False, default=datetime.datetime.now)
    # meta
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

class RegistroValorEstoque(models.Model):
    
    def __unicode__(self):
        return "Registro de estoque em %s no valor de R$%s" % (self.data, self.valor)
    
    class Meta:
        ordering = ('data',)
    
    data = models.DateTimeField(blank=True, default=datetime.datetime.now)
    valor = models.DecimalField("Valor do Estoque", help_text="Valor total do Estoque", max_digits=20, decimal_places=2, default=0)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")


class ControleDeCompra(models.Model):
        
    class Meta:
        ordering = ['-criado']
    
    def __unicode__(self):
        if not self.data_fechado:
            return u"Ordem de Compra #%s ABERTA por funcionário %s em %s" % (self.id, self.funcionario, self.data_aberto)
        else:
            return u"Ordem de Compra #%s FECHADA por funcionário %s em %s" % (self.id, self.funcionario, self.data_aberto)
    
    def proxima_atividade(self):
        proxima = self.atividadedecompra_set.filter(data_fechado=None).order_by('data')
        if proxima:
            return proxima[0]
        else:
            return None

    def atividades_atrasadas(self):
        return self.atividadedecompra_set.filter(data__lte=datetime.datetime.now(), data_fechado=None).all()
    
    def atrasada(self):
        if self.atividadedecompra_set.filter(data__lte=datetime.datetime.now(), data_fechado=None):
            return True
        else:
            return False
    
    def dias_aberto(self):
        if self.data_fechado:
            dias = self.data_aberto - self.data_fechado
            return dias.days
    
    titulo = models.CharField(u"Título", blank=True, max_length=100)
    funcionario = models.ForeignKey('rh.Funcionario', verbose_name=u"Funcionário Responsável", blank=True, null=True)
    data_aberto = models.DateField(blank=True, default=datetime.datetime.today)
    data_fechado = models.DateField("Data de Fechamento", blank=True, null=True)
    descricao = models.TextField(u"Descrição", blank=False)
    fornecedor = models.ForeignKey('FabricanteFornecedor', blank=True, null=True)
    criticidade = models.IntegerField(blank=False, choices=ORDEM_DE_COMPRA_CRITICIDADE_CHOICES, default=0, max_length=1)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

class AtividadeDeCompra(models.Model):
    
    class Meta:
        ordering = ('data',)
    
    def __unicode__(self):
        if not self.data_fechado:
            return "ATIVIDADE #%s/%s ABERTA: %s - %s" % (self.controle_de_compra.id, self.id, self.data, self.descricao)
        else:
            return "ATIVIDADE #%s/%s FECHADA: %s - %s" % (self.controle_de_compra.id, self.id, self.data, self.descricao)
    
    def atrasada(self):
        if self.data > datetime.datetime.now():
            return False
        else:
            # ja foi fechado, nao esta atrasado
            if self.data_fechado:
                return False
            else:
                return True
    
    controle_de_compra = models.ForeignKey('ControleDeCompra')
    data = models.DateTimeField("Data", default=datetime.datetime.now)
    descricao = models.TextField(u"Descrição", blank=False)
    data_fechado = models.DateTimeField(blank=True, null=True)
    fechado_por = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")


class FollowUpRequisicaoCompra(models.Model):
    
    class Meta:
        ordering = ['-criado']
        
        
    def __unicode__(self):
        return u"Follow Up da Requisição #%s" % self.requisicao.id
    
    def data(self):
        return self.criado
        
    class Meta:
        ordering = ['-criado']
    
    requisicao = models.ForeignKey('RequisicaoDeCompra')
    texto = models.TextField(blank=False)
    # registro histórico
    # metadata
    criado_por = models.ForeignKey('rh.Funcionario', related_name="followup_requisicao_adicionado_set",  blank=False, null=False)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")
        
class RequisicaoDeCompra(models.Model):
    
    def __unicode__(self):
        return u"Requisição de Compra ID#%s " % self.id
    
    class Meta:
        ordering = ['-criado']
        
    def ultimo_followup(self):
        if self.followuprequisicaocompra_set.count():
            return self.followuprequisicaocompra_set.all().order_by('-criado')[0]
        else:
            return False

    def clean(self):
        if not self.inicio_atendimento and self.data_solicitado:
            raise ValidationError(u"Erro! Pelo menos uma das datas (Data Para Atender ou Início do Atendimento) devem ser preenchidas.")
    
    atendido = models.BooleanField(default=False)
    atendido_em = models.DateTimeField(blank=True, default=datetime.datetime.now)
    solicitante = models.ForeignKey('rh.Funcionario', related_name="requisicao_de_compra_solicitada")
    solicitado = models.ForeignKey('rh.Funcionario', related_name="requisicao_de_compra_requerida", verbose_name="Funcionário Solicitante")
    inicio_atendimento = models.DateTimeField(blank=True, default=datetime.datetime.now)
    data_solicitado = models.DateField(u"Data para Atender", default=datetime.datetime.today)
    descricao = models.TextField(u"Descrição", blank=False)
    criticidade = models.IntegerField(blank=False, choices=ORDEM_DE_COMPRA_CRITICIDADE_CHOICES, default=0, max_length=1)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

class NotaFiscalLancamentosProducao(models.Model):
    
    class Meta:
        ordering = ['-criado']
    
    def __unicode__(self):
        return u"%s" % self.notafiscal
    
    notafiscal = models.CharField(blank=False, null=False, max_length=100, verbose_name="Nota Fiscal %s" % getattr(settings, 'NOME_EMPRESA', 'Mestria'))
    lancamentos_de_producao = models.ManyToManyField(LancamentoProdProduto, verbose_name=u"Lançamentos de Produção")
    cliente_associado = models.CharField(blank=False, null=False, max_length=100)
    data_saida = models.DateField("Data de Saída", default=datetime.datetime.today)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

class MovimentoEstoqueSubProduto(models.Model):
    
    class Meta:
        ordering = ['-criado']
    
    
    subproduto = models.ForeignKey(SubProduto)
    situacao = models.CharField(blank=False, max_length=100, null=False, choices=SITUACAO_MOVIMENTO_ESTOQUE_SUBPRODUTO_CHOICES, default=0)
    operacao = models.CharField(blank=False, null=False, max_length=100, choices=OPERACAO_MOVIMENTO_ESTOQUE_PRODUTO_CHOICES, default='adiciona')
    quantidade_movimentada = models.IntegerField(blank=False, null=False)
    quantidade_anterior = models.IntegerField(blank=False, null=False)
    quantidade_nova = models.IntegerField(blank=False, null=False)
    justificativa = models.TextField(blank=False, null=False)
    ordem_de_producao = models.ForeignKey(OrdemProducaoSubProduto, blank=True, null=True)
    # meta
    criado_manualmente = models.BooleanField(default=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

class MovimentoEstoqueProduto(models.Model):
    
    class Meta:
        ordering = ['-criado']
        
    produto = models.ForeignKey(ProdutoFinal)
    operacao = models.CharField(blank=True, max_length=100, choices=OPERACAO_MOVIMENTO_ESTOQUE_PRODUTO_CHOICES, default='adiciona')
    quantidade_movimentada = models.IntegerField(blank=False, null=False)
    quantidade_anterior = models.IntegerField(blank=False, null=False)
    quantidade_nova = models.IntegerField(blank=False, null=False)
    justificativa = models.TextField(blank=False, null=False)
    ordem_de_producao = models.ForeignKey(OrdemProducaoProduto, blank=True, null=True)
    registro_de_nota_fiscal = models.ForeignKey('NotaFiscalLancamentosProducao', null=True, blank=True)
    # meta
    criado_manualmente = models.BooleanField(default=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

class FalhaDeTeste(models.Model):
    
    class Meta:
        ordering = ['-criado']
        unique_together = (('tipo', 'codigo'))
        
    def __unicode__(self):
        return "%s - %s: %s" % (self.tipo.upper(), self.codigo, self.descricao)
    
    tipo = models.CharField(blank=False, null=False, max_length=100, choices=TIPO_FALHA_DE_TESTE_CHOICES, default="perda")
    codigo = models.CharField("Código", blank=False, max_length=100)
    descricao = models.TextField(u"Descrição", blank=False, null=False)
    # meta
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

class LancamentoDeFalhaDeTeste(models.Model):
    
    def __unicode__(self):
        return u"Lançamento de Falha para %s" % self.subproduto
    
    def total_perda(self):
        return self.linhalancamentofalhadeteste_set.filter(falha__tipo='perda').aggregate(Sum('quantidade'))['quantidade__sum']
    
    def total_reparo(self):
        return self.linhalancamentofalhadeteste_set.filter(falha__tipo='reparo').aggregate(Sum('quantidade'))['quantidade__sum']

    class Meta:
        ordering = ['-criado']

    subproduto = models.ForeignKey(SubProduto)
    quantidade_total_testada = models.IntegerField(blank=False, null=False, default=0)
    quantidade_funcional_direta = models.IntegerField(blank=False, null=False, default=0)
    quantidade_perdida = models.IntegerField(blank=False, null=False, default=0)
    quantidade_reparada_funcional = models.IntegerField(blank=False, null=False, default=0)
    quantidade_funcional = models.IntegerField(blank=False, null=False, default=0)
    data_lancamento = models.DateField(blank=False, default=datetime.datetime.today, verbose_name=u"Data de Lançamento")
    funcionario_testador = models.ForeignKey('rh.Funcionario', verbose_name=u"Funcionário Testador")
    # meta
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

class LinhaLancamentoFalhaDeTeste(models.Model):
    
    def __unicode__(self):
        return u"Linha do Teste #%s: %s Falhas %s do Sub Produto %s" % \
            (self.lancamento_teste.id, self.quantidade, self.falha, self.lancamento_teste.subproduto)
    
    lancamento_teste = models.ForeignKey(LancamentoDeFalhaDeTeste)
    quantidade = models.IntegerField(blank=False, null=False)
    falha = models.ForeignKey(FalhaDeTeste)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")
    
def subproduto_pre_save(signal, instance, sender, **kwargs):
      ''' Atualiza os campos do subproduto
      '''
      # realiza calculo de custos
      instance.valor_custo_total_linhas = instance.custo_total_linhas()
      instance.valor_custo_total_dos_sub_produtos_agregados = instance.custo_total_dos_sub_produtos_agregados()
      instance.valor_total_de_custo =  instance.valor_custo_total_linhas + instance.valor_custo_total_dos_sub_produtos_agregados
      # recalcula todos os subprodutos que possuem este subproduto como agregado
      for linha in instance.linhasubprodutos_escolhidos.all():
          linha.subproduto_principal.valor_custo_total_linhas = instance.custo_total_linhas()
          linha.subproduto_principal.valor_custo_total_dos_sub_produtos_agregados = instance.custo_total_dos_sub_produtos_agregados()
          linha.subproduto_principal.valor_total_de_custo =  instance.valor_custo_total_linhas + instance.valor_custo_total_dos_sub_produtos_agregados
          linha.subproduto_principal.save()

def componente_post_save(signal, instance, sender, **kwargs):
    # apos salvar cada componente, deverá ser atualizada todas as linhas que ele faz parte
    for opcao in instance.opcaolinhasubproduto_set.filter(padrao=True):
        linha = opcao.linha
        linha.valor_custo_da_linha = linha.custo()
        linha.save()
        linha.subproduto.save()

def opcao_post_save(signal, instance, sender, **kwargs):
    if instance.padrao:
        instance.linha.valor_custo_da_linha = instance.custo()
    instance.linha.save()
# SIGNALS CONNECTION
signals.pre_save.connect(subproduto_pre_save, sender=SubProduto)
signals.post_save.connect(componente_post_save, sender=Componente)
signals.post_save.connect(opcao_post_save, sender=OpcaoLinhaSubProduto)