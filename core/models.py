from django.db import models
from django.utils import timezone

class Empresa(models.Model):
    EmpresaFilial = models.BigIntegerField(primary_key=True)
    emit_CNPJ = models.CharField(null=False, max_length=50)
    emit_xNome = models.CharField(null=False, max_length=100)
    emit_xFant = models.CharField(null=True, max_length=50)
    Mnemonico = models.CharField(null=False, max_length=50)
    emit_xLgr = models.CharField(null=False, max_length=100)
    emit_nro = models.CharField(null=False, max_length=15)
    emit_xCpl = models.CharField(null=True, max_length=50)
    emit_xBairro = models.CharField(null=False, max_length=50)
    emit_cMun = models.BigIntegerField(null=False)
    emit_xMun = models.CharField(null=False, max_length=50)
    emit_cUF = models.BigIntegerField(null=False)
    emit_UF = models.CharField(null=False, max_length=2)
    emit_CEP = models.CharField(null=False, max_length=8)
    emit_cPais = models.BigIntegerField(null=False)
    emit_xPais = models.CharField(null=False, max_length=50)
    emit_IE = models.CharField(null=True, max_length=50)
    emit_IEST = models.CharField(null=True, max_length=50)
    emit_IM = models.CharField(null=True, max_length=50)
    emit_CNAE = models.BigIntegerField(null=False)
    emit_CRT = models.BigIntegerField(null=False)
    emit_eMail = models.CharField(null=True, max_length=255)
    emit_fone = models.CharField(null=True, max_length=11)
    emitDanfe = models.BigIntegerField(null=False)
    emitDanfeZ = models.CharField(null=False, max_length=1)
    ide_mod = models.BigIntegerField(null=False)
    ide_serie = models.BigIntegerField(null=False)
    TipoCert = models.CharField(null=False, max_length=255)
    IdentificacaoAmbiente = models.BigIntegerField(null=False)
    SiglaWebService = models.CharField(null=False, max_length=6)
    WebServiceC = models.CharField(null=False, max_length=6)
    VersaoSchema = models.CharField(null=False, max_length=10)
    Certificado = models.TextField(null=False)
    LicencaDLL = models.CharField(null=False, max_length=255)
    LogoMarca = models.CharField(null=True, max_length=255)
    Logo = models.BooleanField(null=False, default=False)
    smtpserver = models.CharField(null=False, max_length=255)
    smtpserverport = models.BigIntegerField(null=False)
    sendusing = models.BigIntegerField(null=False)
    smtpusessl = models.BooleanField(null=False, default=False)
    smtpauthenticate = models.BigIntegerField(null=False)
    sendusername = models.CharField(null=False, max_length=255)
    sendpassword = models.CharField(null=False, max_length=255)
    smtpconnectiontimeout = models.BigIntegerField(null=False)
    envimsm = models.TextField(null=False)
    EmailContador = models.CharField(null=True, max_length=255)
    DanfeAut = models.BigIntegerField(null=False)
    ChaveSeguranca = models.CharField(null=False, max_length=50)
    sHV = models.BooleanField(null=False, default=False)
    timeUP = models.BigIntegerField(null=False)
    enviarFTP = models.BooleanField(null=False, default=False)
    Proxy = models.CharField(null=True, max_length=255)
    UsuarioProxy = models.CharField(null=True, max_length=255)
    SenhaProxy = models.CharField(null=True, max_length=255)
    CSC = models.CharField(null=True, max_length=100)
    CSCid = models.CharField(null=True, max_length=10)
    Tabela = models.CharField(null=False, max_length=100)
    TabelaItens = models.CharField(null=False, max_length=100)
    TabelaInut = models.CharField(null=False, max_length=100)
    TabelaCSV = models.CharField(null=True, max_length=100)
    Desativado = models.BooleanField(null=False, default=False)
    envimsmBol = models.TextField(null=False)
    envimsmCob = models.TextField(null=False)
    sendusername_greenmotor = models.CharField(null=True, max_length=255)
    sendpassword_greenmotor = models.CharField(null=True, max_length=255)
    Licenca_CTe = models.CharField(null=True, max_length=255)
    Licenca_MDFe = models.CharField(null=True, max_length=255)
    RNTRC = models.CharField(null=True, max_length=8)
    Versao_MDFe = models.CharField(null=True, max_length=10)
    SiglaWebService_MDFe = models.CharField(null=True, max_length=5)
    ide_mod_MDFe = models.BigIntegerField(null=True)
    Tabela_MDFe = models.CharField(null=True, max_length=100)
    CaminhoCert = models.CharField(null=True, max_length=255)
    SenhaCert = models.CharField(null=True, max_length=255)
    Mnemonico_GNRE = models.CharField(null=True, max_length=50)
    CodSegNFCe = models.CharField(null=True, max_length=100)
    idTokenNFCe = models.CharField(null=True, max_length=10)
    URLNFCe = models.CharField(null=True, max_length=255)
    URLChave = models.CharField(null=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'Empresas'

    def __str__(self):
        return str(self.EmpresaFilial) + '|'  + self.Mnemonico

class NFe(models.Model):
    id_nfe = models.AutoField(primary_key=True)
    dtp = models.DateTimeField(null=True, default=timezone.now)
    chave_acesso = models.CharField(null=True, max_length=255)
    recibo_sefaz = models.CharField(null=True, max_length=255)
    status_sefaz = models.CharField(null=True, max_length=255, default='NFe não enviada')
    cStat = models.CharField(null=True, max_length=255)
    xMotivo = models.CharField(null=True, max_length=255)
    nProt = models.CharField(null=True, max_length=255)
    digVal = models.CharField(null=True, max_length=255)
    dhRecbto = models.CharField(null=True, max_length=255)
    dhRegEvento = models.CharField(null=True, max_length=255)
    CodigoBarras = models.CharField(null=True, max_length=255)
    tpEvento = models.CharField(null=True, max_length=255)
    xJust = models.TextField(null=True)
    nSeqEvento = models.CharField(null=True, max_length=255)
    nProtEvento = models.CharField(null=True, max_length=255)
    nCCe = models.IntegerField(null=True)
    idBanco = models.IntegerField(null=True)
    sTP = models.IntegerField(null=True)
    gerBol = models.IntegerField(null=True, default=0)
    frg_xml = models.TextField(null=True)
    referenciar_NF = models.IntegerField(null=True)
    bla = models.CharField(null=True, max_length=255, db_column='[***]')
    ide_cUF = models.IntegerField(null=True, default=35)
    ide_cNF = models.IntegerField(null=True)
    ide_natOp = models.TextField(null=True)
    ide_indPag = models.IntegerField(null=True)
    ide_mod = models.IntegerField(null=True, default=55)
    Pedido = models.BigIntegerField(null=True)
    ide_serie = models.IntegerField(null=True, default=1)
    ide_nNF = models.CharField(null=True, max_length=255, default='0')
    ide_dhEmi = models.CharField(null=True, max_length=25)
    ide_dhSaiEnt = models.CharField(null=True, max_length=25)
    ide_tpNF = models.IntegerField(null=True)
    ide_idDest = models.IntegerField(null=True)
    ide_cMunFG = models.CharField(null=True, max_length=7)
    ide_NFRef = models.TextField(null=True)
    ide_tpImp = models.IntegerField(null=True)
    ide_tpEmis = models.IntegerField(null=True)
    ide_cDV = models.FloatField(null=True)
    ide_tpAmb = models.IntegerField(null=True)
    ide_finNFe = models.IntegerField(null=True)
    ide_indFinal = models.IntegerField(null=True)
    ide_indPres = models.IntegerField(null=True)
    ide_procEmi = models.IntegerField(null=True)
    ide_verProc = models.TextField(null=True)
    ide_dhCont = models.CharField(null=True, max_length=25)
    ide_xJust = models.CharField(null=True, max_length=255)
    ide_indIntermed = models.IntegerField(null=True)
    ide_NFRefs = models.CharField(null=True, max_length=255)
    dest_idEstrangeiro = models.CharField(null=True, max_length=20)
    dest_CNPJ = models.CharField(null=True, max_length=14)
    dest_CPF = models.CharField(null=True, max_length=11)
    dest_xNome = models.CharField(null=True, max_length=255)
    dest_xLgr = models.CharField(null=True, max_length=255)
    dest_nro = models.CharField(null=True, max_length=255)
    dest_xCpl = models.CharField(null=True, max_length=255)
    dest_xBairro = models.CharField(null=True, max_length=255)
    dest_cMun = models.CharField(null=True, max_length=7)
    dest_xMun = models.CharField(null=True, max_length=255)
    dest_UF = models.CharField(null=True, max_length=2)
    dest_CEP = models.CharField(null=True, max_length=8)
    dest_cPais = models.CharField(null=True, max_length=4)
    dest_xPais = models.CharField(null=True, max_length=6)
    dest_fone = models.CharField(null=True, max_length=255)
    dest_indIEDest = models.CharField(null=True, max_length=1)
    dest_IE = models.CharField(null=True, max_length=14)
    dest_ISUF = models.CharField(null=True, max_length=255)
    dest_IM = models.CharField(null=True, max_length=255)
    dest_eMail = models.CharField(null=True, max_length=255)
    entrega_CNPJ = models.CharField(null=True, max_length=14)
    entrega_CPF = models.CharField(null=True, max_length=11)
    entrega_xNome = models.CharField(null=True, max_length=60)
    entrega_xLgr = models.CharField(null=True, max_length=255)
    entrega_nro = models.CharField(null=True, max_length=255)
    entrega_xCpl = models.CharField(null=True, max_length=255)
    entrega_xBairro = models.CharField(null=True, max_length=255)
    entrega_cMun = models.CharField(null=True, max_length=7)
    entrega_xMun = models.CharField(null=True, max_length=255)
    entrega_UF = models.CharField(null=True, max_length=2)
    entrega_CEP = models.CharField(null=True, max_length=8)
    entrega_cPais = models.CharField(null=True, max_length=4)
    entrega_xPais = models.CharField(null=True, max_length=60)
    entrega_fone = models.CharField(null=True, max_length=14)
    entrega_email = models.CharField(null=True, max_length=60)
    entrega_IE = models.CharField(null=True, max_length=14)
    exporta_UFSaidaPais = models.CharField(null=True, max_length=2)
    exporta_xLocEmbarq = models.CharField(null=True, max_length=60)
    exporta_xLocDespacho_Opc = models.CharField(null=True, max_length=60)
    TotalICMS_vBC = models.FloatField(null=True)
    TotalICMS_vICMS = models.FloatField(null=True)
    TotalICMS_vBCST = models.FloatField(null=True)
    TotalICMS_vST = models.FloatField(null=True)
    TotalICMS_vProd = models.FloatField(null=True)
    TotalICMS_vFrete = models.FloatField(null=True)
    TotalICMS_vSeg = models.FloatField(null=True)
    TotalICMS_vDesc = models.FloatField(null=True)
    TotalICMS_vII = models.FloatField(null=True)
    TotalICMS_vIPI = models.FloatField(null=True)
    TotalICMS_vPIS = models.FloatField(null=True)
    TotalICMS_vCOFINS = models.FloatField(null=True)
    TotalICMS_vOutro = models.FloatField(null=True)
    TotalICMS_vNF = models.FloatField(null=True)
    TotalICMS_vTotTrib = models.FloatField(null=True)
    TotalICMS_vICMSDeson = models.FloatField(null=True)
    TotalICMS_vICMSUFDest_Opc = models.FloatField(null=True)
    TotalICMS_vICMSUFRemet_Opc = models.FloatField(null=True)
    TotalICMS_vFCPUFDest_Opc = models.FloatField(null=True)
    TotalICMS_vFCP = models.FloatField(null=True)
    TotalICMS_vFCPST = models.FloatField(null=True)
    TotalICMS_vFCPSTRet = models.FloatField(null=True)
    TotalICMS_vIPIDevol = models.FloatField(null=True)
    transp_modFrete = models.CharField(null=True, max_length=1)
    transporta_CNPJ = models.CharField(null=True, max_length=14)
    transporta_CPF = models.CharField(null=True, max_length=11)
    transporta_xNome = models.CharField(null=True, max_length=255)
    transporta_IE = models.CharField(null=True, max_length=14)
    transporta_xEnder = models.CharField(null=True, max_length=255)
    transporta_xMun = models.CharField(null=True, max_length=255)
    transporta_UF = models.CharField(null=True, max_length=2)
    vol_qVol = models.FloatField(null=True)
    vol_esp = models.CharField(null=True, max_length=255)
    vol_marca = models.CharField(null=True, max_length=255)
    vol_nVol = models.CharField(null=True, max_length=255)
    vol_pesoL = models.FloatField(null=True)
    vol_pesoB = models.FloatField(null=True)
    infAdic_infAdFisco = models.TextField(null=True)
    infAdic_infCpl = models.TextField(null=True)
    infAdic_infTrib = models.TextField(null=True)
    cobr_nFat = models.CharField(null=True, max_length=255)
    cobr_vOrig = models.FloatField(null=True)
    cobr_vDesc = models.FloatField(null=True)
    cobr_vLiq = models.FloatField(null=True)
    pagamento_vTroco_Opc = models.FloatField(null=True)
    TotalICMS_vNF = models.FloatField(null=True)
    NFeRef_refNFe = models.CharField(null=True, max_length=44)
    NFeRef_refNFe_cUF = models.CharField(null=True, max_length=2)
    NFeRef_refNFe_AAMM = models.CharField(null=True, max_length=4)
    NFeRef_refNFe_serie = models.IntegerField(null=True)
    NFeRef_refNFe_nNF = models.CharField(null=True, max_length=255)
    totalISS_vServ_Opc = models.FloatField(null=True)
    totalISS_vBC_Opc = models.FloatField(null=True)
    totalISS_vISS_Opc = models.FloatField(null=True)
    totalISS_vPIS_Opc = models.FloatField(null=True)
    totalISS_vCOFINS_Opc = models.FloatField(null=True)
    totalISS_dCompet = models.CharField(null=True, max_length=10)
    totalISS_vDeducao_Opc = models.FloatField(null=True)
    totalISS_vOutro_Opc = models.FloatField(null=True)
    totalISS_vDescIncond_Opc = models.FloatField(null=True)
    totalISS_vDescCond_Opc = models.FloatField(null=True)
    totalISS_vISSRet_Opc = models.FloatField(null=True)
    totalISS_cRegTrib_Opc = models.CharField(null=True, max_length=1)
    ECFRef_mod = models.CharField(null=True, max_length=2)
    ECFRef_nECF = models.IntegerField(null=True)
    ECFRef_nCOO = models.IntegerField(null=True)
    Caixa_Altura = models.FloatField(null=True)
    Caixa_Largura = models.FloatField(null=True)
    Caixa_Comprimento = models.FloatField(null=True)
    Transmitir = models.BooleanField(null=True, default=False)
    CCe = models.BooleanField(null=True, default=False)
    Cancelar = models.BooleanField(null=True, default=False)
    DataEmissao = models.DateTimeField(null=True, default=timezone.now)
    Usuario = models.CharField(null=True, max_length=50)
    XML_Transmitido = models.BooleanField(null=True, default=False)
    QRCode = models.TextField(null=True)
    ide_cMunFGIBS_Opc = models.CharField(null=True, max_length=7)
    ide_tpNFDebito_Opc = models.IntegerField(null=True)
    ide_tpNFCredito_Opc = models.IntegerField(null=True)
    ide_dPrevEntrega_Opc = models.CharField(null=True, max_length=10)
    compraGov_tpEnteGov = models.IntegerField(null=True)
    compraGov_pRedutor = models.FloatField(null=True)
    compraGov_tpOperGov = models.IntegerField(null=True)
    totalICMS_qBCMono_Opc = models.FloatField(null=True)
    totalICMS_vICMSMono_Opc = models.FloatField(null=True)
    totalICMS_qBCMonoReten_Opc = models.FloatField(null=True)
    totalICMS_vICMSMonoReten_Opc = models.FloatField(null=True)
    totalICMS_qBCMonoRet_Opc = models.FloatField(null=True)
    totalICMS_vICMSMonoRet_Opc = models.FloatField(null=True)
    IBSCBSTot_vBCIBSCBS = models.FloatField(null=True)
    IBSTot_vDif_UF = models.FloatField(null=True)
    IBSTot_vDevTrib_UF = models.FloatField(null=True)
    IBSTot_vIBS_UF = models.FloatField(null=True)
    IBSTot_vDif_Mun = models.FloatField(null=True)
    IBSTot_vDevTrib_Mun = models.FloatField(null=True)
    IBSTot_vIBS_Mun = models.FloatField(null=True)
    IBSTot_vIBS = models.FloatField(null=True)
    IBSTot_vCredPres = models.FloatField(null=True)
    IBSTot_vCredPresCondSus = models.FloatField(null=True)
    CBSTot_vDif = models.FloatField(null=True)
    CBSTot_vDevTrib = models.FloatField(null=True)
    CBSTot_vCBS = models.FloatField(null=True)
    CBSTot_vCredPres = models.FloatField(null=True)
    CBSTot_vCredPresCondSus = models.FloatField(null=True)
    MonoTot_vIBSMono = models.FloatField(null=True)
    MonoTot_vCBSMono = models.FloatField(null=True)
    MonoTot_vIBSMonoReten = models.FloatField(null=True)
    MonoTot_vCBSMonoReten = models.FloatField(null=True)
    MonoTot_vIBSMonoRet = models.FloatField(null=True)
    MonoTot_vCBSMonoRet = models.FloatField(null=True)
    EstornoCred_vIBSEstCred = models.FloatField(null=True)
    EstornoCred_vCBSEstCred = models.FloatField(null=True)
    totalRTC_vIS = models.FloatField(null=True)
    totalRTC_vNFTot = models.FloatField(null=True)
    tribRet_vRetPIS = models.FloatField(null=True)
    tribRet_vRetCOFINS = models.FloatField(null=True)
    tribRet_vRetCSLL = models.FloatField(null=True)
    tribRet_vBCIRRF = models.FloatField(null=True)
    tribRet_vIRRF = models.FloatField(null=True)
    tribRet_vBCRetPrev = models.FloatField(null=True)
    tribRet_vRetPrev = models.FloatField(null=True)
    NFAntePgto_chaveNFe = models.CharField(null=True, max_length=255)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.Pedido) + '|' + self.ide_nNF

class GreenMotor_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'GreenMotor_NFE_400'

class GreenMotor_SC_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'GreenMotor_SC_NFE_400'

class Infinity_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'Infinity_NFE_400'

class LanmaxLog_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'LanmaxLog_NFE_400'

class LanmaxPecas_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'LanmaxPecas_NFE_400'

class Liberty_CE_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'Liberty_CE_NFE_400'

class Liberty_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'Liberty_NFE_400'

class LPBlumenau_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'LPBlumenau_NFE_400'

class Maxipecas_Filial_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'Maxipecas_Filial_NFE_400'

class Maxipecas_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'Maxipecas_NFE_400'

class PortoReal_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'PortoReal_NFE_400'

class Rio_BA_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'Rio_BA_NFE_400'

class Rio_MG_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'Rio_MG_NFE_400'

class Rio_MT_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'Rio_MT_NFE_400'

class Rio_PR_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'Rio_PR_NFE_400'

class Rio_RJ_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'Rio_RJ_NFE_400'

class Rio_RS_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'Rio_RS_NFE_400'

class Starte_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'Starte_NFE_400'

class Starte_SC_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'Starte_SC_NFE_400'

class Starte_MG_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'Starte_MG_NFE_400'

class TNL_Blumenau_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'TNL_Blumenau_NFE_400'

class TNL_Caruaru_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'TNL_Caruaru_NFE_400'

class TNL_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'TNL_NFE_400'

class Vialuna_NFE_400(NFe):
    class Meta:
        managed = False
        db_table = 'Vialuna_NFE_400'

class NFeItens(models.Model):
    id_item = models.AutoField(primary_key=True)
    id_nfe = models.BigIntegerField(null=True)
    det_nItem = models.CharField(null=True, max_length=4)
    det_infAdprod = models.TextField(null=True)
    det_pDevol_Opc = models.FloatField(null=True)
    det_vIPIDevol_Opc = models.FloatField(null=True)
    prod_cProd = models.CharField(max_length=255, null=True)
    prod_cEAN = models.CharField(null=True, max_length=14)
    prod_xProd = models.CharField(max_length=120, null=True)
    prod_NCM = models.CharField(max_length=8, null=True)
    prod_NVE_Opc = models.CharField(null=True, max_length=255)
    prod_CEST_Opc = models.CharField(null=True, max_length=7)
    prod_indEscala_Opc = models.CharField(null=True, max_length=1)
    prod_CNPJFab_Opc = models.CharField(null=True, max_length=14)
    prod_cBenef_Opc = models.CharField(null=True, max_length=10)
    prod_EXTIPI = models.CharField(null=True, max_length=3)
    prod_CFOP = models.BigIntegerField(null=True)
    prod_uCOM = models.CharField(max_length=10, null=True)
    prod_qCOM = models.BigIntegerField(null=True)
    prod_vUnCOM = models.FloatField(null=True)
    prod_vProd = models.FloatField(null=True)
    prod_cEANTrib = models.CharField(null=True, max_length=14)
    prod_uTrib = models.CharField(null=True, max_length=2)
    prod_qTrib = models.FloatField(null=True)
    prod_vUnTrib = models.FloatField(null=True)
    prod_vFrete = models.FloatField(null=True)
    prod_vSeg = models.FloatField(null=True)
    prod_vDesc = models.FloatField(null=True)
    prod_vOutro = models.FloatField(null=True)
    prod_indTot = models.IntegerField(null=True)
    prod_xPed = models.CharField(null=True, max_length=15)
    prod_nItemPed = models.CharField(null=True, max_length=6)
    prod_nFCI_Opc = models.CharField(null=True, max_length=36)
    imp_vTotTrib = models.FloatField(null=True)
    icms_orig = models.CharField(max_length=1, null=True)
    icms_CST = models.CharField(max_length=3, null=True)
    icms_modBC = models.IntegerField(null=True)
    icms_pRedBC = models.FloatField(null=True)
    icms_vBC = models.FloatField(null=True)
    icms_pICMS = models.FloatField(null=True)
    icms_vICMS = models.FloatField(null=True)
    icms_vBCFCP = models.FloatField(null=True)
    icms_pFCP = models.FloatField(null=True)
    icms_vFCP = models.FloatField(null=True)
    icms_vBCFCPST = models.FloatField(null=True)
    icms_pFCPST = models.FloatField(null=True)
    icms_vFCPST = models.FloatField(null=True)
    icms_vBCFCPSTRet = models.FloatField(null=True)
    icms_pFCPSTRet = models.FloatField(null=True)
    icms_vFCPSTRet = models.FloatField(null=True)
    icms_pST = models.FloatField(null=True)
    icms_vICMSSubstituto = models.FloatField(null=True)
    icms_modBCST = models.IntegerField(null=True)
    icms_pMVAST = models.FloatField(null=True)
    icms_pRedBCST = models.FloatField(null=True)
    icms_vBCST = models.FloatField(null=True)
    icms_pICMSST = models.FloatField(null=True)
    icms_vICMSST = models.FloatField(null=True)
    icms_vBCSTRet = models.FloatField(null=True)
    icms_vICMSSTRet = models.FloatField(null=True)
    icms_vBCSTDest = models.FloatField(null=True)
    icms_vICMSSTDest = models.FloatField(null=True)
    icms_motDesICMS = models.IntegerField(null=True)
    icms_pBCOp = models.FloatField(null=True)
    icms_UFST = models.CharField(null=True, max_length=2)
    icms_pCredSN = models.FloatField(null=True)
    icms_vCredICMSSN = models.FloatField(null=True)
    icms_vICMSDeson = models.FloatField(null=True)
    icms_vICMSOp = models.FloatField(null=True)
    icms_pDif = models.FloatField(null=True)
    icms_vICMSDif = models.FloatField(null=True)
    ICMSUFDest_vBCUFDest = models.FloatField(null=True)
    ICMSUFDest_vBCFCPUFDest_Opc = models.FloatField(null=True)
    ICMSUFDest_pFCPUFDest = models.FloatField(null=True)
    ICMSUFDest_pICMSUFDest = models.FloatField(null=True)
    ICMSUFDest_pICMSInter = models.FloatField(null=True)
    ICMSUFDest_pICMSInterPart = models.FloatField(null=True)
    ICMSUFDest_vFCPUFDest = models.FloatField(null=True)
    ICMSUFDest_vICMSUFDest = models.FloatField(null=True)
    ICMSUFDest_vICMSUFRemet = models.FloatField(null=True)
    pis_CST = models.CharField(null=True, max_length=2)
    pis_vBC = models.FloatField(null=True)
    pis_pPIS = models.FloatField(null=True)
    pis_vPIS = models.FloatField(null=True)
    pis_qBCProd = models.FloatField(null=True)
    pis_vAliqProd = models.FloatField(null=True)
    cofins_CST = models.CharField(null=True, max_length=2)
    cofins_vBC = models.FloatField(null=True)
    cofins_pCOFINS = models.FloatField(null=True)
    cofins_vCOFINS = models.FloatField(null=True)
    cofins_qBCProd = models.FloatField(null=True)
    cofins_vAliqProd = models.FloatField(null=True)
    IPI_clEnq = models.CharField(null=True, max_length=5)
    IPI_CNPJProd = models.CharField(null=True, max_length=14)
    IPI_cSelo = models.CharField(null=True, max_length=60)
    IPI_qSelo = models.FloatField(null=True)
    IPI_cEnq = models.CharField(null=True, max_length=3)
    IPI_CST = models.CharField(null=True, max_length=2)
    IPI_vBC = models.FloatField(null=True)
    IPI_pIPI = models.FloatField(null=True)
    IPI_vIPI = models.FloatField(null=True)
    IPI_qUnid = models.FloatField(null=True)
    IPI_vUnid = models.FloatField(null=True)
    DI_nDI = models.CharField(null=True, max_length=15)
    DI_dDI = models.CharField(null=True, max_length=10)
    DI_xLocDesemb = models.CharField(null=True, max_length=60)
    DI_UFDesemb = models.CharField(null=True, max_length=2)
    DI_dDesemb = models.CharField(null=True, max_length=10)
    DI_tpViaTransp = models.IntegerField(null=True)
    DI_vAFRMM_Opc = models.FloatField(null=True)
    DI_tpIntermedio = models.IntegerField(null=True)
    DI_CNPJ_Opc = models.CharField(null=True, max_length=14)
    DI_UFTerceiro_Opc = models.CharField(null=True, max_length=2)
    DI_cExportador = models.CharField(null=True, max_length=60)
    adi_nAdicao = models.IntegerField(null=True)
    adi_nSeqAdic = models.IntegerField(null=True)
    adi_cFabricante = models.CharField(null=True, max_length=60)
    adi_vDescDI = models.FloatField(null=True)
    II_vBC = models.FloatField(null=True)
    II_vII = models.FloatField(null=True)
    II_vDespAdu = models.FloatField(null=True)
    II_vIOF = models.FloatField(null=True)
    icms_pFCPDif = models.FloatField(null=True)
    icms_vFCPDif = models.FloatField(null=True)
    icms_vFCPEfet = models.FloatField(null=True)
    icms_vICMSSTDeson = models.FloatField(null=True)
    icms_motDesICMSST = models.IntegerField(null=True)
    NumSerie = models.CharField(null=True, max_length=500)
    CodProd = models.IntegerField(null=True)
    icms_indDeduzDeson = models.IntegerField(null=True)
    icms_cBenefRBC = models.CharField(null=True, max_length=255)
    indBemMovelUsado_Opc = models.IntegerField(null=True)
    tpCredPresIBSZFM_Opc = models.IntegerField(null=True)
    det_vItem = models.FloatField(null=True)
    chaveAcessoRef = models.CharField(null=True, max_length=255)
    cCredPresumido = models.CharField(null=True, max_length=255)
    pCredPresumido = models.FloatField(null=True)
    vCredPresumido = models.FloatField(null=True)
    IS_CST = models.CharField(null=True, max_length=255)
    IS_cClassTrib = models.CharField(null=True, max_length=255)
    IS_vBC = models.FloatField(null=True)
    IS_pIS = models.FloatField(null=True)
    IS_vIS = models.FloatField(null=True)
    IS_pISEspec_Opc = models.FloatField(null=True)
    IS_uTrib_Opc = models.CharField(null=True, max_length=255)
    IS_qTrib_Opc = models.FloatField(null=True)
    IBSCBS_CST = models.CharField(null=True, max_length=255)
    IBSCBS_cClassTrib = models.CharField(null=True, max_length=255)
    IBSCBS_indDoacao_Opc = models.CharField(null=True, max_length=255)
    IBSCBS_vBC = models.FloatField(null=True)
    gIBSUF_pIBSUF = models.FloatField(null=True)
    gIBSUF_pDif_Opc = models.FloatField(null=True)
    gIBSUF_vDif_Opc = models.FloatField(null=True)
    gIBSUF_vDevTrib_Opc = models.FloatField(null=True)
    gIBSUF_pRedAliq_Opc = models.FloatField(null=True)
    gIBSUF_pAliqEfet_Opc = models.FloatField(null=True)
    gIBSUF_vIBSUF = models.FloatField(null=True)
    gIBSMun_pIBSMun = models.FloatField(null=True)
    gIBSMun_pDif_Opc = models.FloatField(null=True)
    gIBSMun_vDif_Opc = models.FloatField(null=True)
    gIBSMun_vDevTrib_Opc = models.FloatField(null=True)
    gIBSMun_pRedAliq_Opc = models.FloatField(null=True)
    gIBSMun_pAliqEfet_Opc = models.FloatField(null=True)
    gIBSMun_vIBSMun = models.FloatField(null=True)
    IBSCBS_vIBS = models.FloatField(null=True)
    gCBS_pCBS = models.FloatField(null=True)
    gCBS_pDif_Opc = models.FloatField(null=True)
    gCBS_vDif_Opc = models.FloatField(null=True)
    gCBS_vDevTrib_Opc = models.FloatField(null=True)
    gCBS_pRedAliq_Opc = models.FloatField(null=True)
    gCBS_pAliqEfet_Opc = models.FloatField(null=True)
    gCBS_vCBS = models.FloatField(null=True)
    gTribRegular_CSTReg = models.CharField(null=True, max_length=255)
    gTribRegular_cClassTribReg = models.CharField(null=True, max_length=255)
    gTribRegular_pAliqEfetRegIBSUF = models.FloatField(null=True)
    gTribRegular_vTribRegIBSUF = models.FloatField(null=True)
    gTribRegular_pAliqEfetRegIBSMun = models.FloatField(null=True)
    gTribRegular_vTribRegIBSMun = models.FloatField(null=True)
    gTribRegular_pAliqEfetRegCBS = models.FloatField(null=True)
    gTribRegular_vTribRegCBS = models.FloatField(null=True)
    gTribCompraGov_pAliqIBSUF = models.FloatField(null=True)
    gTribCompraGov_vTribIBSUF = models.FloatField(null=True)
    gTribCompraGov_pAliqIBSMun = models.FloatField(null=True)
    gTribCompraGov_vTribIBSMun = models.FloatField(null=True)
    gTribCompraGov_pAliqCBS = models.FloatField(null=True)
    gTribCompraGov_vTribCBS = models.FloatField(null=True)
    gIBSCBSMono_qBCMono_Opc = models.FloatField(null=True)
    gIBSCBSMono_adRemIBS_Opc = models.FloatField(null=True)
    gIBSCBSMono_adRemCBS_Opc = models.FloatField(null=True)
    gIBSCBSMono_vIBSMono_Opc = models.FloatField(null=True)
    gIBSCBSMono_vCBSMono_Opc = models.FloatField(null=True)
    gIBSCBSMono_qBCMonoReten_Opc = models.FloatField(null=True)
    gIBSCBSMono_adRemIBSReten_Opc = models.FloatField(null=True)
    gIBSCBSMono_vIBSMonoReten_Opc = models.FloatField(null=True)
    gIBSCBSMono_adRemCBSReten_Opc = models.FloatField(null=True)
    gIBSCBSMono_vCBSMonoReten_Opc = models.FloatField(null=True)
    gIBSCBSMono_qBCMonoRet_Opc = models.FloatField(null=True)
    gIBSCBSMono_adRemIBSRet_Opc = models.FloatField(null=True)
    gIBSCBSMono_vIBSMonoRet_Opc = models.FloatField(null=True)
    gIBSCBSMono_adRemCBSRet_Opc = models.FloatField(null=True)
    gIBSCBSMono_vCBSMonoRet_Opc = models.FloatField(null=True)
    gIBSCBSMono_pDifIBS_Opc = models.FloatField(null=True)
    gIBSCBSMono_vIBSMonoDif_Opc = models.FloatField(null=True)
    gIBSCBSMono_pDifCBS_Opc = models.FloatField(null=True)
    gIBSCBSMono_vCBSMonoDif_Opc = models.FloatField(null=True)
    gIBSCBSMono_vTotIBSMonoItem = models.FloatField(null=True)
    gIBSCBSMono_vTotCBSMonoItem = models.FloatField(null=True)
    gTransfCred_vIBS = models.FloatField(null=True)
    gTransfCred_vCBS = models.FloatField(null=True)
    gAjusteCompet_competApur = models.CharField(null=True, max_length=255)
    gAjusteCompet_vIBS = models.FloatField(null=True)
    gAjusteCompet_vCBS = models.FloatField(null=True)
    gEstornoCred_vIBSEstCred = models.FloatField(null=True)
    gEstornoCred_vCBSEstCred = models.FloatField(null=True)
    gCredPresOper_vBCCredPres = models.FloatField(null=True)
    gCredPresOper_cCredPres = models.CharField(null=True, max_length=255)
    gCredPresOper_pIBSCredPres_Opc = models.FloatField(null=True)
    gCredPresOper_vIBSCredPres_Opc = models.FloatField(null=True)
    gCredPresOper_vIBSCredPresCondSus_Opc = models.FloatField(null=True)
    gCredPresOper_pCBSCredPres_Opc = models.FloatField(null=True)
    gCredPresOper_vCBSCredPres_Opc = models.FloatField(null=True)
    gCredPresOper_vCBSCredPresCondSus_Opc = models.FloatField(null=True)
    gCredPresIBSZFM_competApur = models.CharField(null=True, max_length=255)
    gCredPresIBSZFM_tpCredPresIBSZFM = models.FloatField(null=True)
    gCredPresIBSZFM_vCredPresIBSZFM = models.FloatField(null=True)
    ref_nItem = models.IntegerField(null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.id_nfe)

class Starte_NFEItens_400(NFeItens):
    class Meta:
        managed = False
        db_table = 'Starte_NFEItens_400'

class Starte_SC_NFEItens_400(NFeItens):
    class Meta:
        managed = False
        db_table = 'Starte_SC_NFEItens_400'

class Starte_MG_NFEItens_400(NFeItens):
    class Meta:
        managed = False
        db_table = 'Starte_MG_NFEItens_400'

class TNL_NFEItens_400(NFeItens):
    class Meta:
        managed = False
        db_table = 'TNL_NFEItens_400'

class TNL_Caruaru_NFEItens_400(NFeItens):
    class Meta:
        managed = False
        db_table = 'TNL_Caruaru_NFEItens_400'

class LanmaxLog_NFEItens_400(NFeItens):
    class Meta:
        managed = False
        db_table = 'LanmaxLog_NFEItens_400'

class Maxipecas_NFEItens_400(NFeItens):
    class Meta:
        managed = False
        db_table = 'Maxipecas_NFEItens_400'

class Maxipecas_Filial_NFEItens_400(NFeItens):
    class Meta:
        managed = False
        db_table = 'Maxipecas_Filial_NFEItens_400'

class LanmaxPecas_NFEItens_400(NFeItens):
    class Meta:
        managed = False
        db_table = 'LanmaxPecas_NFEItens_400'

class LPBlumenau_NFEItens_400(NFeItens):
    class Meta:
        managed = False
        db_table = 'LPBlumenau_NFEItens_400'

class PortoReal_NFEItens_400(NFeItens):
    class Meta:
        managed = False
        db_table = 'PortoReal_NFEItens_400'

class Vialuna_NFEItens_400(NFeItens):
    class Meta:
        managed = False
        db_table = 'Vialuna_NFEItens_400'

class Infinity_NFEItens_400(NFeItens):
    class Meta:
        managed = False
        db_table = 'Infinity_NFEItens_400'

class Liberty_NFEItens_400(NFeItens):
    class Meta:
        managed = False
        db_table = 'Liberty_NFEItens_400'

class Liberty_CE_NFEItens_400(NFeItens):
    class Meta:
        managed = False
        db_table = 'Liberty_CE_NFEItens_400'
        
class GreenMotor_NFEItens_400(NFeItens):
    class Meta:
        managed = False
        db_table = 'GreenMotor_NFEItens_400'

class Rio_BA_NFEItens_400(NFeItens):
    class Meta:
        managed = False
        db_table = 'Rio_BA_NFEItens_400'

class Rio_RS_NFEItens_400(NFeItens):
    class Meta:
        managed = False
        db_table = 'Rio_RS_NFEItens_400'

class Rio_PR_NFEItens_400(NFeItens):
    class Meta:
        managed = False
        db_table = 'Rio_PR_NFEItens_400'

class Rio_MG_NFEItens_400(NFeItens):
    class Meta:
        managed = False
        db_table = 'Rio_MG_NFEItens_400'

class Rio_RJ_NFEItens_400(NFeItens):
    class Meta:
        managed = False
        db_table = 'Rio_RJ_NFEItens_400'

class Rio_MT_NFEItens_400(NFeItens):
    class Meta:
        managed = False
        db_table = 'Rio_MT_NFEItens_400'

class Diretorio(models.Model):
    ID = models.AutoField(primary_key=True)
    CNPJ = models.CharField(null=False, max_length=14)
    TipoArquivo = models.CharField(null=False, max_length=50)
    Diretorio = models.CharField(null=False, max_length=255)

    class Meta:
        managed = False
        db_table = 'Diretorios'

    def __str__(self):
        return self.CNPJ

class FormasPagto_NFE(models.Model):
    id = models.AutoField(primary_key=True)
    id_nfe = models.BigIntegerField(null=False)
    ide_serie = models.CharField(null=False, max_length=2)
    pagamento_nForma = models.IntegerField(null=False)
    pagamento_indPag_Opc = models.IntegerField(null=True)
    pagamento_tPag = models.CharField(null=True, max_length=2)
    pagamento_vPag = models.FloatField(null=True)
    pagamento_tpIntegra_Opc = models.CharField(null=True, max_length=2)
    pagamento_CNPJ_Opc = models.CharField(null=True, max_length=14)
    pagamento_tBand_Opc = models.CharField(null=True, max_length=2)
    pagamento_cAut_Opc = models.CharField(null=True, max_length=20)

    class Meta:
        managed = False
        db_table = 'FormasPagto_NFE'

    def __str__(self):
        return str(self.id_nfe) + '|' + str(self.ide_serie)

class InstrBol(models.Model):
    CodInstr = models.AutoField(primary_key=True)
    Instrucao = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'InstrBol'

    def __str__(self):
        return str(self.CodInstr) + '|' + self.Instrucao

class Intermediador(models.Model):
    CNPJ = models.CharField(primary_key=True, max_length=14)
    idCadIntTran = models.CharField(max_length=60)

    class Meta:
        managed = False
        db_table = 'Intermediadores'

    def __str__(self):
        return self.CNPJ

class GNRE_DetalhamentoReceitas(models.Model):
    ID = models.AutoField(primary_key=True)
    Codigo = models.CharField(max_length=6)
    UF = models.CharField(max_length=2)
    Receita = models.BigIntegerField()
    Descricao = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'GNRE_DetalhamentoReceitas_200'

    def __str__(self):
        return str(self.ID)
    
class GNRE_Receitas(models.Model):
    ID = models.AutoField(primary_key=True)
    UF = models.CharField(max_length=2)
    Codigo = models.BigIntegerField()
    Descricao = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'GNRE_Receitas_200'

    def __str__(self):
        return str(self.ID)
    
class GNRE_DocumentosOrigem(models.Model):
    ID = models.AutoField(primary_key=True)
    Codigo = models.BigIntegerField()
    UF = models.CharField(max_length=2)
    Receita = models.BigIntegerField()
    Descricao = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'GNRE_DocumentosOrigem_200'

    def __str__(self):
        return str(self.ID)
    
class GNRE_Produtos(models.Model):
    ID = models.AutoField(primary_key=True)
    UF = models.CharField(max_length=2)
    Codigo = models.BigIntegerField()
    Receita = models.BigIntegerField()
    Descricao = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'GNRE_Produtos_200'

    def __str__(self):
        return str(self.ID)
    
class GNRE_CamposVisiveis(models.Model):
    ID = models.AutoField(primary_key=True)
    UF = models.CharField(max_length=2)
    Receita = models.BigIntegerField()
    TemPeriodoRef = models.BooleanField(default=False)
    TemPeriodo = models.BooleanField(default=False)
    TemInfoDest = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'GNRE_CamposVisiveis_200'

    def __str__(self):
        return str(self.ID)
    
class GNRE_CamposAdicionais(models.Model):
    ID = models.AutoField(primary_key=True)
    UF = models.CharField(max_length=2)
    Receita = models.BigIntegerField()
    Codigo = models.BigIntegerField()
    Titulo = models.CharField(max_length=100)
    Tipo = models.CharField(max_length=1)
    Obrigatorio = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'GNRE_CamposAdicionais_200'

    def __str__(self):
        return str(self.ID)
    
class GNRE_InfBoleto(models.Model):
    Protocolo = models.CharField(max_length=20)
    UF_Favorecida = models.CharField(max_length=2)
    Receita = models.CharField(max_length=6)
    emit_CGC = models.CharField(max_length=16)
    emit_RazaoSocial = models.CharField(max_length=100)
    emit_Endereco = models.CharField(max_length=100)
    emit_Municipio = models.CharField(max_length=50)
    emit_UF = models.CharField(max_length=2)
    emit_CEP = models.CharField(max_length=8)
    emit_Tel = models.CharField(max_length=11)
    dest_CGC = models.CharField(max_length=16)
    dest_Municipio = models.CharField(max_length=50)
    Produto = models.CharField(max_length=100)
    Data_Vencto = models.CharField(max_length=10)
    Data_Pagto = models.CharField(max_length=10)
    NFe = models.CharField(max_length=9)
    MesAnoRef = models.CharField(max_length=7)
    InfCompl = models.CharField(max_length=300)
    Valor = models.FloatField()
    Att_Mon = models.FloatField()
    Juros = models.FloatField()
    Multa = models.FloatField()
    ValorGNRE = models.FloatField()
    LinhaDigitavel = models.CharField(max_length=60)
    CodBar = models.CharField(max_length=50)
    NumControle = models.CharField(max_length=16)
    qtdVias = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'GNRE_InfBoleto'

    def __str__(self):
        return str(self.ID)
    
class GNRE_QtdVias(models.Model):
    UF = models.CharField(max_length=2)
    Receita = models.BigIntegerField()
    QtdVias = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'GNRE_QtdVias'

    def __str__(self):
        return str(self.ID)
    
class TabMunicipios(models.Model):
    ID = models.AutoField(primary_key=True)
    IDUF = models.CharField(max_length=2)
    NOME = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'TAB_MUNICIPIOS'

    def __str__(self):
        return str(self.ID)
    
class TabUF(models.Model):
    ID = models.AutoField(primary_key=True)
    NOME = models.CharField(max_length=50)
    UF = models.CharField(max_length=2)
    ATIVO_GNRE = models.BooleanField(default=0)

    class Meta:
        managed = False
        db_table = 'TAB_UF'

    def __str__(self):
        return str(self.ID)