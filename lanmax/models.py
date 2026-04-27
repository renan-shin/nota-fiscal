from django.db import models
from django.utils import timezone

class Conta(models.Model):
    Conta = models.CharField(primary_key=True, max_length=8)
    Referência = models.CharField(null=True, max_length=50)
    Ag = models.IntegerField(null=True)
    CC = models.IntegerField(null=True)
    Digito = models.IntegerField(null=True)
    UltimoNossoNum = models.BigIntegerField(null=True)
    CarteiraCob = models.IntegerField(null=True)
    Empresa = models.BigIntegerField(null=False)
    client_id = models.CharField(null=True, max_length=255)
    client_secret = models.CharField(null=True, max_length=255)
    caminho_arquivo_crt = models.CharField(null=True, max_length=255)
    caminho_arquivo_key = models.CharField(null=True, max_length=255)
    client_id_boleto = models.CharField(null=True, max_length=255)
    client_secret_boleto = models.CharField(null=True, max_length=255)
    caminho_arquivo_crt_boleto = models.CharField(null=True, max_length=255)
    caminho_arquivo_key_boleto = models.CharField(null=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'Contas'

    def __str__(self):
        return self.Conta

class EmpresaFilial(models.Model):
    empresa_filial = models.BigIntegerField(primary_key=True, db_column='EmpresaFilial')
    mnemonico = models.CharField(null=False, max_length=15, db_column='Mnemonico')
    cnpj = models.CharField(null=True, max_length=14, db_column='CNPJ')
    conta_cobranca = models.ForeignKey(Conta, null=True, on_delete=models.CASCADE, db_column='ContaCobranca')

    class Meta:
        managed = False
        db_table = 'EmpresaFilial'

    def __str__(self):
        return str(self.empresa_filial) + '|'  + self.mnemonico

class Transportadora(models.Model):
    cod_transp = models.BigIntegerField(primary_key=True, db_column='CodTransp')
    nome = models.CharField(null=False, max_length=50, db_column='Nome')
    razao_social = models.CharField(null=False, max_length=100, db_column='RazaoSocial')
    cnpj = models.CharField(null=True, max_length=14, db_column='CNPJ')
    inscr_estadual = models.CharField(null=True, max_length=20, db_column='InscrEstadual')

    class Meta:
        managed = False
        db_table = 'Transportadoras'

    def __str__(self):
        return str(self.cod_transp) + '|'  + self.nome

class Cliente(models.Model):
    cod_cliente = models.DecimalField(primary_key=True, max_digits=24, decimal_places=6, db_column='CodCliente')
    nome = models.CharField(null=False, max_length=30, db_column='Nome')
    razao_social = models.CharField(null=False, max_length=80, db_column='RazaoSocial')
    cod_transp = models.ForeignKey(Transportadora, null=False, on_delete=models.CASCADE, db_column='CodTransp')
    inscricao_estadual = models.CharField(max_length=20, null=True, db_column='IE')

    class Meta:
        managed = False
        db_table = 'Clientes'

    def __str__(self):
        return str(self.cod_cliente) + '|'  + self.nome

class Pedido(models.Model):
    cod_pedido = models.BigIntegerField(primary_key=True, db_column='CodPedido')
    cod_cliente = models.ForeignKey(Cliente, null=False, on_delete=models.CASCADE, db_column='CodCliente')
    empresa_filial = models.ForeignKey(EmpresaFilial, null=False, on_delete=models.CASCADE, db_column='EmpresaFilial')
    cod_transp = models.ForeignKey(Transportadora, null=False, on_delete=models.CASCADE, db_column='CodTransp')
    controle_interno = models.BooleanField(default=False, db_column='ControleInterno')
    num_nota_fiscal = models.BigIntegerField(db_column='NumNotaFiscal')
    gnre_protocolo = models.CharField(max_length=20, null=True, db_column='GNRE_Protocolo')
    difal_protocolo = models.CharField(max_length=20, null=True, db_column='DIFAL_Protocolo')
    fcp_protocolo = models.CharField(max_length=20, null=True, db_column='FCP_Protocolo')

    class Meta:
        managed = False
        db_table = 'Pedidos'

    def __str__(self):
        return str(self.cod_pedido)
    
class Pagamento(models.Model):
    cod_pedido = models.BigIntegerField(primary_key=True, db_column='CodPedido')
    num_parcela = models.CharField(max_length=20, null=False, db_column='NumParcela')
    vencimento = models.DateTimeField(null=False, default=timezone.now, db_column='Vencimento')
    conta = models.CharField(max_length=8, null=True, db_column='Conta')
    forma = models.CharField(max_length=7, null=False, db_column='Forma')

    class Meta:
        managed = False
        db_table = 'Pagamentos'

    def __str__(self):
        return str(self.cod_pedido) + '|' + self.num_parcela

class Constante(models.Model):
    CodConst = models.AutoField(primary_key=True)
    Constante = models.CharField(max_length=255)
    Classe = models.CharField(max_length=30)
    Tipo = models.CharField(max_length=30)
    Descricao = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'aux_Constantes'

    def __str__(self):
        return str(self.CodConst)
    
class GNRE_Pagamentos(models.Model):
    CodPedido = models.BigIntegerField(null=False, db_column='CodPedido')
    Tipo = models.CharField(max_length=5, null=False)
    NFe = models.CharField(max_length=9, null=False)
    Empresa = models.CharField(max_length=50, null=False)
    Status = models.IntegerField(null=False)
    UF = models.CharField(max_length=2, null=False)
    Protocolo = models.CharField(max_length=20, null=True)
    Num_Controle = models.CharField(max_length=50, null=True)
    DataEmissao = models.DateTimeField(null=True, default=timezone.now)
    DataValidacao = models.DateTimeField(null=True, default=timezone.now)
    DataPagamento = models.DateTimeField(null=True, default=timezone.now)
    Valor = models.DecimalField(max_digits=21, decimal_places=2, null=False)
    Comprovante = models.CharField(max_length=255, null=True)
    Obs = models.CharField(max_length=255, null=True)
    Enviado = models.BooleanField(default=False, null=False)

    class Meta:
        managed = False
        db_table = 'GNRE_Pagamentos'

    def __str__(self):
        return str(self.CodPedido) + '|' + self.Tipo + '|' + self.NFe + '|' + str(self.Status)
    
class EmailsAEnviar(models.Model):
    id = models.AutoField(primary_key=True)
    email_to = models.CharField(max_length=255, null=False)
    email_cc = models.CharField(max_length=255, null=True)
    assunto = models.CharField(max_length=255, null=False)
    email_body = models.TextField(null=False)
    body_format = models.CharField(max_length=255, null=False)
    attachments = models.TextField(null=True)
    data = models.DateTimeField(null=False, default=timezone.now)
    status = models.BooleanField(default=False, null=False)

    class Meta:
        managed = False
        db_table = 'EmailsAEnviar'

    def __str__(self):
        return str(id)