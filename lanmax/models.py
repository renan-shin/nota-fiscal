from django.db import models

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
    token_temporario = models.TextField(null=True)

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

    class Meta:
        managed = False
        db_table = 'Pedidos'

    def __str__(self):
        return str(self.cod_pedido)

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