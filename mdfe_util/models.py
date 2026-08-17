from django.db import models
from django.utils import timezone

class MDFe_Proprietarios(models.Model):
    id = models.AutoField(primary_key=True)
    cpf = models.CharField(null=True, max_length=11)
    cnpj = models.CharField(null=True, max_length=14)
    rntrc = models.CharField(null=False, max_length=8)
    razao_social = models.CharField(null=False, max_length=60)
    ie = models.CharField(null=True, max_length=14)
    uf = models.CharField(null=True, max_length=2)
    tp_prop = models.IntegerField(null=False)

    class Meta:
        managed = False
        db_table = 'MDFe_Proprietarios'

    def __str__(self):
        return str(self.id)

class MDFe_Veiculos(models.Model):
    id = models.AutoField(primary_key=True)
    marca = models.CharField(null=False, max_length=255)
    modelo = models.CharField(null=False, max_length=255)
    renavam = models.CharField(null=False, max_length=11)
    placa = models.CharField(null=False, max_length=7)
    capacidade_kg = models.IntegerField(null=True)
    capacidade_m3 = models.IntegerField(null=True)
    tipo_rodado = models.CharField(null=False, max_length=2)
    tipo_carroceria = models.CharField(null=False, max_length=2)
    uf = models.CharField(null=False, max_length=2)
    id_proprietario = models.ForeignKey(MDFe_Proprietarios, null=False, on_delete=models.CASCADE, db_column='id_proprietario')
    ativo = models.BooleanField(null=False, default=True)
    EmpresaFilial = models.IntegerField(null=True)

    class Meta:
        managed = False
        db_table = 'MDFe_Veiculos'

    def __str__(self):
        return str(self.id)

class MDFe_Motoristas(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(null=False, max_length=255)
    cpf = models.CharField(null=False, max_length=11)
    ativo = models.BooleanField(null=False, default=True)

    class Meta:
        managed = False
        db_table = 'MDFe_Motoristas'

    def __str__(self):
        return str(self.id)

class MDFe(models.Model):
    id_mdfe = models.AutoField(primary_key=True)
    data_criacao = models.DateTimeField(null=False, default=timezone.now)
    chave_acesso = models.CharField(null=True, max_length=255)
    status = models.CharField(null=False, max_length=255, default='MDFe não enviada')
    recibo = models.CharField(null=True, max_length=255)
    cStat = models.IntegerField(null=True)
    digVal = models.CharField(null=True, max_length=255)
    dhRecbto = models.CharField(null=True, max_length=255)
    nProt = models.CharField(null=True, max_length=255)
    xJust = models.CharField(null=True, max_length=255)
    nProtocoloCanc = models.CharField(null=True, max_length=255)
    dProtocoloCanc = models.CharField(null=True, max_length=25)
    cUFEnc = models.CharField(null=True, max_length=2)
    cMunEnc = models.CharField(null=True, max_length=7)
    nProtocoloEnc = models.CharField(null=True, max_length=255)
    dProtocoloEnc = models.CharField(null=True, max_length=25)
    tpEvento = models.CharField(null=True, max_length=255)
    nSeqEvento = models.IntegerField(null=True)
    ide_tpAmb = models.IntegerField(null=False, default=1)
    ide_tpEmit = models.IntegerField(null=False, default=2)
    ide_tpTransp_Opc = models.IntegerField(null=True)
    ide_mod = models.IntegerField(null=False, default=58)
    ide_serie = models.IntegerField(null=False, default=0)
    ide_nMDF = models.CharField(null=False, max_length=9, default='0')
    ide_cMDF = models.CharField(null=True, max_length=255)
    ide_cDV = models.IntegerField(null=True)
    ide_modal = models.CharField(null=False, max_length=1, default='1')
    ide_dhEmi = models.CharField(null=True, max_length=25)
    ide_tpEmis = models.IntegerField(null=False, default=1)
    ide_procEmi = models.IntegerField(null=False, default=0)
    ide_verProc = models.CharField(null=False, max_length=20, default='1.1')
    ide_UFIni = models.CharField(null=True, max_length=2)
    ide_UFFim = models.CharField(null=True, max_length=2)
    total_qCTe_Opc = models.IntegerField(null=False, default=0)
    total_qNFe_Opc = models.IntegerField(null=False, default=0)
    total_qMDFe_Opc = models.IntegerField(null=False, default=0)
    total_vCarga = models.DecimalField(null=False, max_digits=15, decimal_places=2, default=0.00)
    total_cUnid = models.CharField(null=False, max_length=2, default='01')
    total_qCarga = models.DecimalField(null=False, max_digits=15, decimal_places=4, default=0.0000)
    qrCode = models.CharField(null=True, max_length=255)
    infAdFisco_Opc = models.TextField(null=True)
    infCpl_Opc = models.TextField(null=True)
    id_veiculo = models.ForeignKey(MDFe_Veiculos, null=False, on_delete=models.CASCADE, db_column='id_veiculo')
    id_condutor = models.ForeignKey(MDFe_Motoristas, null=False, on_delete=models.CASCADE, db_column='id_condutor')

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.id_mdfe)

class MDFe_LanmaxLog(MDFe):
    class Meta:
        managed = False
        db_table = 'MDFe_LanmaxLog'

class MDFe_Starte(MDFe):
    class Meta:
        managed = False
        db_table = 'MDFe_Starte'

class MDFe_ChaveNFe(models.Model):
    id = models.AutoField(primary_key=True)
    id_mdfe = models.BigIntegerField(null=False)
    ide_serie = models.IntegerField(null=False)
    chave_nfe = models.CharField(null=False, max_length=255)
    cMunCarrega = models.IntegerField(null=False)
    xMunCarrega = models.CharField(null=False, max_length=255)
    cMunDescarrega = models.IntegerField(null=False)
    xMunDescarrega = models.CharField(null=False, max_length=255)
    ValorNFe = models.DecimalField(null=False, default=0.00, max_digits=15, decimal_places=2)
    PesoNFe = models.DecimalField(null=False, max_digits=15, decimal_places=4, default=0.0000)

    class Meta:
        managed = False
        db_table = 'MDFe_ChaveNFe'

    def __str__(self):
        return str(self.id)

class MDFe_Percursos(models.Model):
    id = models.AutoField(primary_key=True)
    id_mdfe = models.BigIntegerField(null=False)
    ide_serie = models.IntegerField(null=False)
    uf = models.CharField(null=False, max_length=2)
    ordem = models.IntegerField(null=False, default=0)

    class Meta:
        managed = False
        db_table = 'MDFe_Percursos'

    def __str__(self):
        return str(self.id)

class MDFe_Diretorios(models.Model):
    id = models.AutoField(primary_key=True)
    cnpj = models.CharField(null=False, max_length=14)
    tipo_arquivo = models.CharField(null=False, max_length=50)
    diretorio = models.CharField(null=False, max_length=255)

    class Meta:
        managed = False
        db_table = 'MDFe_Diretorios'

    def __str__(self):
        return str(self.id)