# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'QuantidadeDeMarca.marca'
        db.alter_column(u'comercial_quantidadedemarca', 'marca_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['comercial.Marca'], null=True))

    def backwards(self, orm):

        # Changing field 'QuantidadeDeMarca.marca'
        db.alter_column(u'comercial_quantidadedemarca', 'marca_id', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['comercial.Marca']))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'cadastro.bairro': {
            'Meta': {'object_name': 'Bairro'},
            'cidade': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cadastro.Cidade']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'cadastro.cidade': {
            'Meta': {'object_name': 'Cidade'},
            'estado': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'cadastro.cliente': {
            'Meta': {'object_name': 'Cliente'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'cnpj': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'contato': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'cpf': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'fantasia': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'funcionario_responsavel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Funcionario']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_referencia': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'inscricao_estadual': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'nascimento': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'observacao': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'origem': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cadastro.ClienteOrigem']", 'null': 'True', 'blank': 'True'}),
            'ramo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cadastro.Ramo']", 'null': 'True', 'blank': 'True'}),
            'rg': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'solicitar_consulta_credito': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'telefone_celular': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'telefone_fixo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'})
        },
        u'cadastro.clienteorigem': {
            'Meta': {'object_name': 'ClienteOrigem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'observacao': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'cadastro.precliente': {
            'Meta': {'object_name': 'PreCliente'},
            'adicionado_por': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'precliente_lancado_set'", 'to': u"orm['auth.User']"}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'cliente_convertido': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cadastro.Cliente']", 'null': 'True', 'blank': 'True'}),
            'contato': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'dados': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        u'cadastro.ramo': {
            'Meta': {'object_name': 'Ramo'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'comercial.categoriacontratofechado': {
            'Meta': {'object_name': 'CategoriaContratoFechado'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'comercial.contratofechado': {
            'Meta': {'object_name': 'ContratoFechado'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'categoria': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['comercial.CategoriaContratoFechado']"}),
            'cliente': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cadastro.Cliente']"}),
            'concluido': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'forma_pagamento': ('django.db.models.fields.CharField', [], {'default': "'dinheiro'", 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inicio_cobranca': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 8, 14, 0, 0)'}),
            'objeto': ('django.db.models.fields.TextField', [], {}),
            'parcelas': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'receber_apos_conclusao': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'responsavel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Funcionario']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'emaberto'", 'max_length': '100'}),
            'tipo': ('django.db.models.fields.CharField', [], {'default': "'fechado'", 'max_length': '100'}),
            'valor': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'valor_entrada': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'})
        },
        u'comercial.linharecursohumano': {
            'Meta': {'object_name': 'LinhaRecursoHumano'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'cargo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Cargo']"}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'orcamento': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['comercial.Orcamento']"}),
            'quantidade': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'comercial.linharecursomaterial': {
            'Meta': {'object_name': 'LinhaRecursoMaterial'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'orcamento': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['comercial.Orcamento']"}),
            'produto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['estoque.Produto']"}),
            'quantidade': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'comercial.marca': {
            'Meta': {'object_name': 'Marca'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'comercial.modelo': {
            'Meta': {'object_name': 'Modelo'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'comercial.orcamento': {
            'Meta': {'object_name': 'Orcamento'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'cliente': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cadastro.Cliente']", 'null': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'descricao': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modelo': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'precliente': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cadastro.PreCliente']", 'null': 'True', 'blank': 'True'})
        },
        u'comercial.perfilacessocomercial': {
            'Meta': {'object_name': 'PerfilAcessoComercial'},
            'analista': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'gerente': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'comercial.propostacomercial': {
            'Meta': {'object_name': 'PropostaComercial'},
            'adicionado_por': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'proposta_adicionada_set'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'cliente': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cadastro.Cliente']", 'null': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'data_expiracao': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 8, 29, 0, 0)'}),
            'follow_up': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'observacoes': ('django.db.models.fields.TextField', [], {}),
            'orcamento_vinculado': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['comercial.Orcamento']", 'null': 'True', 'blank': 'True'}),
            'precliente': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cadastro.PreCliente']", 'null': 'True', 'blank': 'True'}),
            'probabilidade': ('django.db.models.fields.IntegerField', [], {'default': '50', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'aberta'", 'max_length': '100', 'blank': 'True'}),
            'valor_fechado': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'valor_proposto': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'})
        },
        u'comercial.quantidadedemarca': {
            'Meta': {'object_name': 'QuantidadeDeMarca'},
            'contratofechado': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['comercial.ContratoFechado']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marca': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['comercial.Marca']", 'null': 'True', 'blank': 'True'}),
            'modelo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['comercial.Modelo']"}),
            'quantidade': ('django.db.models.fields.IntegerField', [], {})
        },
        u'comercial.tipodecontratofechado': {
            'Meta': {'object_name': 'TipodeContratoFechado'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'estoque.produto': {
            'Meta': {'object_name': 'Produto'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'codigo': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'descricao': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'fator': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'icms': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ncm': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'preco_custo': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'preco_venda': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'quantidade_em_estoque': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'substituicao_tributaria_valor': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tabela': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['estoque.TabelaDePreco']", 'null': 'True', 'blank': 'True'}),
            'tipo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['estoque.TipoDeProduto']", 'null': 'True', 'blank': 'True'}),
            'tributacao': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'unidade_de_compra': ('django.db.models.fields.CharField', [], {'default': "'un'", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'unidade_de_venda': ('django.db.models.fields.CharField', [], {'default': "'un'", 'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'estoque.tabeladepreco': {
            'Meta': {'object_name': 'TabelaDePreco'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'percentual': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'})
        },
        u'estoque.tipodeproduto': {
            'Meta': {'object_name': 'TipoDeProduto'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'rh.cargo': {
            'Meta': {'object_name': 'Cargo'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'competencias': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['rh.Competencia']", 'symmetrical': 'False'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'departamento': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Departamento']"}),
            'descricao': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'dias_renovacao_exames': ('django.db.models.fields.IntegerField', [], {'default': '365'}),
            'exame_medico_padrao': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['rh.TipoDeExameMedico']", 'symmetrical': 'False'}),
            'gratificacao': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'periculosidade': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'salario_referencia': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'})
        },
        u'rh.competencia': {
            'Meta': {'object_name': 'Competencia'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'rh.departamento': {
            'Meta': {'object_name': 'Departamento'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'rh.funcionario': {
            'Meta': {'ordering': "['nome']", 'object_name': 'Funcionario'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'bairro': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cadastro.Bairro']"}),
            'cargo_atual': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'funcionario_cargo_atual_set'", 'null': 'True', 'to': u"orm['rh.Cargo']"}),
            'cargo_inicial': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'funcionario_cargo_inicial_set'", 'to': u"orm['rh.Cargo']"}),
            'carteira_habilitacao_categoria': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'carteira_habilitacao_expedicao': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'carteira_habilitacao_numero': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'carteira_habilitacao_vencimento': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'carteira_profissional_emissao': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'carteira_profissional_numero': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'carteira_profissional_serie': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'cep': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'certificado_reservista': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'competencias': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['rh.Competencia']", 'null': 'True', 'blank': 'True'}),
            'complemento': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'cpf': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'escolaridade_conclusao': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 8, 14, 0, 0)', 'null': 'True', 'blank': 'True'}),
            'escolaridade_cursos': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'escolaridade_nivel': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'escolaridade_serie_inconclusa': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'estado_civil': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'forma_de_pagamento': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'foto': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'funcionario_superior': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Funcionario']", 'null': 'True', 'blank': 'True'}),
            'gratificacao': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'local_de_trabalho': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'membro_cipa': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'nacionalidade': ('django.db.models.fields.CharField', [], {'default': "'Brasil'", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'nascimento': ('django.db.models.fields.DateField', [], {}),
            'naturalidade': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'nome_companheiro': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'nome_mae': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'nome_pai': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'numero': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'numero_lre': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'observacao': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'periodo_trabalhado_corrente': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'periodo_trabalhado_corrente'", 'unique': 'True', 'null': 'True', 'to': u"orm['rh.PeriodoTrabalhado']"}),
            'pis': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'residencia': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'rg': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'rg_data': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'rg_expeditor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'rua': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'salario_atual': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'salario_inicial': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'sexo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'telefone_celular': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'telefone_fixo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'telefone_recado': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'titulo_eleitor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'valor_aluguel': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'valor_hora': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'})
        },
        u'rh.periodotrabalhado': {
            'Meta': {'ordering': "['-criado']", 'object_name': 'PeriodoTrabalhado'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'fim': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Funcionario']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inicio': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 8, 14, 0, 0)'})
        },
        u'rh.tipodeexamemedico': {
            'Meta': {'object_name': 'TipoDeExameMedico'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'descricao': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'valor': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'})
        }
    }

    complete_apps = ['comercial']