from core.models import *
from django.apps import apps
from django.db import connection
from django.conf import settings
import win32com.client, os

obj_nfe_util = win32com.client.Dispatch("NFe_Util_2G.Util")

def tem_difal(id_nfe, empresa_filial):
    empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
    nome_tabela = apps.get_model('core', empresa.Tabela)
    nfe = nome_tabela.objects.get(id_nfe=id_nfe)

    if nfe.dest_indIEDest == 9 and nfe.ide_idDest == 2 and nfe.ide_indFinal == 1:
        return True
    
    return False

def isEmpRio(empresa):
    if empresa.ide_serie in(8, 81, 82, 83, 84, 85):
        return True

    return False

def temBol(id_nfe, empresa_filial):
    empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
    nome_tabela = apps.get_model('core', empresa.Tabela)
    nfe = nome_tabela.objects.get(id_nfe=id_nfe)
    cursor = connection.cursor()

    if int(nfe.Pedido) < 100000000:
        if isEmpRio(empresa):
            cursor.execute("SELECT * FROM GreenMotor.dbo.Pagamentos WHERE CodPedido = %s AND Forma = %s", [nfe.Pedido, 'BOL',])
        else:
            cursor.execute("SELECT * FROM GreenMotor.dbo.Pagamentos WHERE CodPedido = %s AND Forma = %s AND Conta NOT LIKE %s AND Conta NOT LIKE %s", [nfe.Pedido, 'BOL', '%Rio%', 'Ometz%',])
    else:
        cursor.execute("SELECT * FROM Lanmax.dbo.Pagamentos WHERE CodPedido = %s AND Forma = %s AND Conta NOT LIKE %s AND Conta NOT LIKE %s", [nfe.Pedido, 'BOL', '%Rio%', 'Ometz%',])

    rows = cursor.fetchall()
    
    if len(rows) > 0:
        return True

    return False

def consulta_status_2g(empresa):
    msg_dados = ''
    msg_ret_ws = ''
    msg_resultado = ''
    proxy = ''
    usuario = ''
    senha = ''

    return obj_nfe_util.ConsultaStatus2G(
        empresa.SiglaWebService,
        empresa.emit_UF,
        empresa.IdentificacaoAmbiente,
        empresa.Certificado,
        empresa.VersaoSchema,
        msg_dados,
        msg_ret_ws,
        msg_resultado,
        proxy,
        usuario,
        senha
    )

def ide(id_nfe, empresa_filial):
    empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
    nome_tabela = apps.get_model('core', empresa.Tabela)

    nfe = nome_tabela.objects.get(id_nfe=id_nfe)
    ide_nfref = ''

    if nfe.referenciar_NF == 2:
        ide_nfref = obj_nfe_util.NFRef(
            nfe.NFeRef_refNFe_cUF,
            nfe.NFeRef_refNFe_AAMM,
            empresa.emit_CNPJ,
            1,
            nfe.NFeRef_refNFe_serie,
            nfe.NFeRef_refNFe_nNF
        )
    elif nfe.referenciar_NF == 1:
        chaves_referenciada = nfe.ide_NFRefs.split(';')

        for chave in chaves_referenciada:
            ide_nfref += obj_nfe_util.nfeRef(chave)
    
    return obj_nfe_util.identificador202006(
        nfe.ide_cUF if nfe.ide_cUF else 0,
        nfe.ide_cNF if nfe.ide_cNF else 0,
        nfe.ide_natOp if nfe.ide_natOp else '',
        nfe.ide_mod if nfe.ide_mod else 55,
        nfe.ide_serie if nfe.ide_serie else 0,
        nfe.ide_nNF if nfe.ide_nNF else 0,
        nfe.ide_dhEmi if nfe.ide_dhEmi else '',
        nfe.ide_dhSaiEnt if nfe.ide_dhSaiEnt else '',
        nfe.ide_tpNF if nfe.ide_tpNF else 1,
        nfe.ide_idDest if nfe.ide_idDest else 1,
        nfe.ide_cMunFG if nfe.ide_cMunFG else '',
        ide_nfref.replace(' ', ''),
        nfe.ide_tpImp if nfe.ide_tpImp else 1,
        nfe.ide_tpEmis if nfe.ide_tpEmis else 1,
        nfe.ide_cDV if nfe.ide_cDV else 0,
        nfe.ide_tpAmb if nfe.ide_tpAmb else 1,
        nfe.ide_finNFe if nfe.ide_finNFe else 1,
        nfe.ide_indFinal if nfe.ide_indFinal else 0,
        nfe.ide_indPres if nfe.ide_indPres else 0,
        nfe.ide_procEmi if nfe.ide_procEmi else 0,
        nfe.ide_verProc if nfe.ide_verProc else '',
        nfe.ide_dhCont if nfe.ide_dhCont else '',
        nfe.ide_xJust if nfe.ide_dhCont else '',
        nfe.ide_indIntermed if nfe.ide_indIntermed else 0
    )

def emit(empresa_filial):
    empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)

    return obj_nfe_util.emitente2G(
        empresa.emit_CNPJ,
        '',# empresa.emit_CPF,
        empresa.emit_xNome,
        empresa.emit_xFant,
        empresa.emit_xLgr,
        empresa.emit_nro,
        empresa.emit_xCpl,
        empresa.emit_xBairro,
        empresa.emit_cMun,
        empresa.emit_xMun,
        empresa.emit_UF,
        empresa.emit_CEP,
        empresa.emit_cPais,
        empresa.emit_xPais,
        empresa.emit_fone,
        empresa.emit_IE,
        empresa.emit_IEST if empresa.emit_IEST else '',
        empresa.emit_IM if empresa.emit_IM else '',
        empresa.emit_CNAE if empresa.emit_IM else '',
        empresa.emit_CRT
    )

def dest(id_nfe, empresa_filial):
    empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
    nome_tabela = apps.get_model('core', empresa.Tabela)
    nfe = nome_tabela.objects.get(id_nfe=id_nfe)

    if nfe.sTP == 1:
        dest_CPF = nfe.dest_CPF
        dest_CNPJ = ''
    elif nfe.sTP == 2:
        dest_CNPJ = nfe.dest_CNPJ
        dest_CPF = ''

    return obj_nfe_util.destinatario310(
        dest_CNPJ,
        dest_CPF,
        nfe.dest_idEstrangeiro if nfe.dest_idEstrangeiro else '',
        nfe.dest_xNome.replace('&', '&amp;') if nfe.dest_xNome else '',
        nfe.dest_xLgr if nfe.dest_xLgr else '',
        nfe.dest_nro.replace('&', '&amp;') if nfe.dest_nro else '',
        nfe.dest_xCpl.replace('&', '&amp;') if nfe.dest_xCpl else '',
        nfe.dest_xBairro if nfe.dest_xBairro else '',
        nfe.dest_cMun if nfe.dest_cMun else '',
        nfe.dest_xMun if nfe.dest_xMun else '',
        nfe.dest_UF if nfe.dest_UF else '',
        nfe.dest_CEP if nfe.dest_CEP else '',
        nfe.dest_cPais if nfe.dest_cPais else '',
        nfe.dest_xPais if nfe.dest_xPais else '',
        nfe.dest_fone if nfe.dest_fone else '',
        nfe.dest_indIEDest if nfe.dest_indIEDest else 1,
        nfe.dest_IE if nfe.dest_IE else '',
        nfe.dest_ISUF if nfe.dest_ISUF else '',
        nfe.dest_IM if nfe.dest_IM else '',
        nfe.dest_eMail if nfe.dest_eMail else ''
    )

def det_prod(id_nfe, empresa_filial):
    empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
    nome_tabela = apps.get_model('core', empresa.Tabela)
    nome_tabela_itens = apps.get_model('core', empresa.TabelaItens)
    nfe = nome_tabela.objects.get(id_nfe=id_nfe)
    itens_nfe = list(nome_tabela_itens.objects.filter(id_nfe=id_nfe).order_by('id_item'))

    produtos = ''

    for item in itens_nfe:
        det_infAdprod = ''
        prod_di = ''

        if not item.det_infAdprod:
            det_infAdprod = item.NumSerie if item.NumSerie else ''
        else:
            det_infAdprod += '|' + item.NumSerie if item.NumSerie else ''

        if item.prod_CFOP >= 3101 and item.prod_CFOP <= 3129:
            nADI = obj_nfe_util.adi310(
                item.adi_nAdicao if item.adi_nAdicao else 0,
                item.adi_nSeqAdic if item.adi_nSeqAdic else 0,
                item.adi_cFabricante if item.adi_cFabricante else '',
                item.adi_vDescDI if item.adi_vDescDI else 0,
                '' # nDraw_Opc
            )

            prod_di = obj_nfe_util.DI310(
                item.DI_nDI if item.DI_nDI else '',
                item.DI_dDI if item.DI_dDI else '',
                item.DI_xLocDesemb if item.DI_xLocDesemb else '',
                item.DI_UFDesemb if item.DI_UFDesemb else '',
                item.DI_dDesemb if item.DI_dDesemb else '',
                item.DI_tpViaTransp if item.DI_tpViaTransp else 0,
                item.DI_vAFRMM_Opc if item.DI_vAFRMM_Opc else 0,
                item.DI_tpIntermedio if item.DI_tpIntermedio else 0,
                item.DI_CNPJ_Opc if item.DI_CNPJ_Opc else '',
                item.DI_UFTerceiro_Opc if item.DI_UFTerceiro_Opc else '',
                item.DI_cExportador if item.DI_cExportador else '',
                nADI
            )

        det_produto = obj_nfe_util.produto400(
            item.prod_cProd if item.prod_cProd else '',
            item.prod_cEAN if item.prod_cEAN else '',
            item.prod_xProd.replace('&', '&amp;') if item.prod_xProd else '',
            item.prod_NCM if item.prod_NCM else '',
            item.prod_NVE_Opc if item.prod_NVE_Opc else '',
            item.prod_CEST_Opc if item.prod_CEST_Opc else '',
            item.prod_indEscala_Opc if item.prod_indEscala_Opc else '',
            item.prod_CNPJFab_Opc if item.prod_CNPJFab_Opc else '',
            item.prod_cBenef_Opc if item.prod_cBenef_Opc else '',
            item.prod_EXTIPI if item.prod_EXTIPI else '',
            item.prod_CFOP if item.prod_CFOP else '',
            item.prod_uCOM if item.prod_uCOM else 0,
            item.prod_qCOM if item.prod_qCOM else 0,
            item.prod_vUnCOM if item.prod_vUnCOM else 0,
            item.prod_vProd if item.prod_vProd else 0,
            item.prod_cEANTrib if item.prod_cEANTrib else '',
            item.prod_uTrib if item.prod_uTrib else 0,
            item.prod_qTrib if item.prod_qTrib else 0,
            item.prod_vUnTrib if item.prod_vUnTrib else 0,
            item.prod_vFrete if item.prod_vFrete else 0,
            item.prod_vSeg if item.prod_vSeg else 0,
            item.prod_vDesc if item.prod_vDesc else 0,
            item.prod_vOutro if item.prod_vOutro else 0,
            item.prod_indTot if item.prod_indTot else 1,
            prod_di,
            '', # prod_DetExp
            '', # prod_DetEspec
            item.prod_xPed if item.prod_xPed else '',
            item.prod_nItemPed if item.prod_nItemPed else '',
            item.prod_nFCI_Opc if item.prod_nFCI_Opc else '',
            '' # rastro
        )

        if (item.icms_CST == '60' or item.icms_CST == '500') and nfe.ide_indFinal == 0:
            det_ICMS = obj_nfe_util.icmsEfetNT201805(
                item.icms_orig if item.icms_orig else '',
                item.icms_CST if item.icms_CST else '',
                item.icms_vBCSTRet if item.icms_vBCSTRet else 0.001,
                item.icms_pST if item.icms_pST else 0,
                item.icms_vICMSSubstituto if item.icms_vICMSSubstituto else 0.001,
                item.icms_vICMSSTRet if item.icms_vICMSSTRet else 0.001,
                0, # icms_vBCFCPSTRet
                0, # icms_modBCST
                0, # icms_pMVAST
                0, # icms_pRedBCST
                0, # icms_vBCST
                0, # icms_pICMSST
                0, # icms_vICMSST
                0, # icms_vBCSTRet
                0 #icms_vICMSSTRet
            )
        else:
            det_ICMS = obj_nfe_util.icmsNT2023004(
                item.icms_orig if item.icms_orig else '',
                item.icms_CST if item.icms_CST else '',
                item.icms_modBC if item.icms_modBC else 0,
                item.icms_pRedBC if item.icms_pRedBC else 0,
                item.icms_vBC if item.icms_vBC else 0,
                item.icms_pICMS if item.icms_pICMS else 0,
                item.icms_vICMS if item.icms_vICMS else 0,
                item.icms_modBCST if item.icms_modBCST else 0,
                item.icms_pMVAST if item.icms_pMVAST else 0,
                item.icms_pRedBCST if item.icms_pRedBCST else 0,
                item.icms_vBCST if item.icms_vBCST else 0,
                item.icms_pICMSST if item.icms_pICMSST else 0,
                item.icms_vICMSST if item.icms_vICMSST else 0,
                item.icms_vBCSTRet if item.icms_vBCSTRet else 0,
                item.icms_vICMSSTRet if item.icms_vICMSSTRet else 0,
                item.icms_vBCSTDest if item.icms_vBCSTDest else 0,
                item.icms_vICMSSTDest if item.icms_vICMSSTDest else 0,
                item.icms_motDesICMS if item.icms_motDesICMS else 0,
                item.icms_pBCOp if item.icms_pBCOp else 0,
                item.icms_UFST if item.icms_UFST else '',
                item.icms_pCredSN if item.icms_pCredSN else 0,
                item.icms_vCredICMSSN if item.icms_vCredICMSSN else 0,
                item.icms_vICMSDeson if item.icms_vICMSDeson else 0,
                item.icms_vICMSOp if item.icms_vICMSOp else 0,
                item.icms_pDif if item.icms_pDif else 0,
                item.icms_vICMSDif if item.icms_vICMSDif else 0,
                item.icms_vBCFCP if item.icms_vBCFCP else 0,
                item.icms_pFCP if item.icms_pFCP else 0,
                item.icms_vFCP if item.icms_vFCP else 0,
                item.icms_vBCFCPST if item.icms_vBCFCPST else 0,
                item.icms_pFCPST if item.icms_pFCPST else 0,
                item.icms_vFCPST if item.icms_vFCPST else 0,
                item.icms_vBCFCPSTRet if item.icms_vBCFCPSTRet else 0,
                item.icms_pFCPSTRet if item.icms_pFCPSTRet else 0,
                item.icms_vFCPSTRet if item.icms_vFCPSTRet else 0,
                item.icms_pST if item.icms_pST else 0,
                item.icms_pFCPDif if item.icms_pFCPDif else 0,
                item.icms_vFCPDif if item.icms_vFCPDif else 0,
                item.icms_vFCPEfet if item.icms_vFCPEfet else 0,
                item.icms_vICMSSTDeson if item.icms_vICMSSTDeson else 0,
                item.icms_motDesICMSST if item.icms_motDesICMSST else 0,
                item.icms_indDeduzDeson if item.icms_indDeduzDeson else 0,
                item.icms_cBenefRBC if item.icms_cBenefRBC else ''
            )

        det_PIS = obj_nfe_util.pis(
            item.pis_CST if item.pis_CST else '99',
            item.pis_vBC if item.pis_vBC else 0,
            item.pis_pPIS if item.pis_pPIS else 0,
            item.pis_vPIS if item.pis_vPIS else 0,
            item.pis_qBCProd if item.pis_qBCProd else 0,
            item.pis_vAliqProd if item.pis_vAliqProd else 0
        )

        det_COFINS = obj_nfe_util.cofins(
            item.cofins_CST if item.cofins_CST else '99',
            item.cofins_vBC if item.cofins_vBC else 0,
            item.cofins_pCOFINS if item.cofins_pCOFINS else 0,
            item.cofins_vCOFINS if item.cofins_vCOFINS else 0,
            item.cofins_qBCProd if item.cofins_qBCProd else 0,
            item.cofins_vAliqProd if item.cofins_vAliqProd else 0
        )

        if tem_difal(id_nfe, empresa_filial) and empresa.emit_CRT == 3:
            det_ICMSUFDest = obj_nfe_util.ICMSUFDest400(
                item.ICMSUFDest_vBCUFDest if item.ICMSUFDest_vBCUFDest else 0,
                item.ICMSUFDest_vBCFCPUFDest_Opc if item.ICMSUFDest_vBCFCPUFDest_Opc else 0,
                item.ICMSUFDest_pFCPUFDest if item.ICMSUFDest_pFCPUFDest else 0,
                item.ICMSUFDest_pICMSUFDest if item.ICMSUFDest_pICMSUFDest else 0,
                item.ICMSUFDest_pICMSInter if item.ICMSUFDest_pICMSInter else 0,
                item.ICMSUFDest_pICMSInterPart if item.ICMSUFDest_pICMSInterPart else 0,
                item.ICMSUFDest_vFCPUFDest if item.ICMSUFDest_vFCPUFDest else 0,
                item.ICMSUFDest_vICMSUFDest if item.ICMSUFDest_vICMSUFDest else 0,
                item.ICMSUFDest_vICMSUFRemet if item.ICMSUFDest_vICMSUFRemet else 0
            )
        else:
            det_ICMSUFDest = ''

        det_IPI = obj_nfe_util.IPI400(
            item.IPI_CNPJProd if item.IPI_CNPJProd else '',
            item.IPI_cSelo if item.IPI_cSelo else '',
            item.IPI_qSelo if item.IPI_qSelo else 0,
            item.IPI_cEnq if item.IPI_cEnq else '999',
            item.IPI_CST if item.IPI_CST else '99',
            item.IPI_vBC if item.IPI_vBC else 0,
            item.IPI_pIPI if item.IPI_pIPI else 0,
            item.IPI_vIPI if item.IPI_vIPI else 0,
            item.IPI_qUnid if item.IPI_qUnid else 0,
            item.IPI_vUnid if item.IPI_vUnid else 0
        )

        if item.prod_CFOP >= 3101 and item.prod_CFOP <= 3129:
            det_II = obj_nfe_util.II(
                item.II_vBC if item.II_vBC else 0,
                item.II_vII if item.II_vII else 0,
                item.II_vDespAdu if item.II_vDespAdu else 0,
                item.II_vIOF if item.II_vIOF else 0
            )
        else:
            det_II = ''

        det_PISST = ''
        det_COFINSST = ''
        det_ISSQN = ''

        det_imposto = obj_nfe_util.impostoNT2015003(
            item.imp_vTotTrib if item.imp_vTotTrib else 0,
            det_ICMS,
            det_IPI,
            det_II,
            det_PIS,
            det_COFINS,
            det_PISST,
            det_COFINSST,
            det_ISSQN,
            det_ICMSUFDest
        )

        det_obsContItem = obj_nfe_util.obsCont('', '')
        det_obsFiscoItem = obj_nfe_util.obsCont('', '')

        produtos += obj_nfe_util.detalheNT2021004(
            item.det_nItem if item.det_nItem else 0,
            det_produto,
            det_imposto,
            det_infAdprod,
            item.det_pDevol_Opc if item.det_pDevol_Opc else 0,
            item.det_vIPIDevol_Opc if item.det_vIPIDevol_Opc else 0,
            det_obsContItem,
            det_obsFiscoItem
        )

    return produtos

def GTotal_NFe(id_nfe, empresa_filial):
    empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
    nome_tabela = apps.get_model('core', empresa.Tabela)
    nfe = nome_tabela.objects.get(id_nfe=id_nfe)

    ICMSTot = obj_nfe_util.totalICMS400(
        nfe.TotalICMS_vBC if nfe.TotalICMS_vBC else 0,
        nfe.TotalICMS_vICMS if nfe.TotalICMS_vICMS else 0,
        nfe.TotalICMS_vBCST if nfe.TotalICMS_vBCST else 0,
        nfe.TotalICMS_vST if nfe.TotalICMS_vST else 0,
        nfe.TotalICMS_vProd if nfe.TotalICMS_vProd else 0,
        nfe.TotalICMS_vFrete if nfe.TotalICMS_vFrete else 0,
        nfe.TotalICMS_vSeg if nfe.TotalICMS_vSeg else 0,
        nfe.TotalICMS_vDesc if nfe.TotalICMS_vDesc else 0,
        nfe.TotalICMS_vII if nfe.TotalICMS_vII else 0,
        nfe.TotalICMS_vIPI if nfe.TotalICMS_vIPI else 0,
        nfe.TotalICMS_vPIS if nfe.TotalICMS_vPIS else 0,
        nfe.TotalICMS_vCOFINS if nfe.TotalICMS_vCOFINS else 0,
        nfe.TotalICMS_vOutro if nfe.TotalICMS_vOutro else 0,
        nfe.TotalICMS_vNF if nfe.TotalICMS_vNF else 0,
        nfe.TotalICMS_vTotTrib if nfe.TotalICMS_vTotTrib else 0,
        nfe.TotalICMS_vICMSDeson if nfe.TotalICMS_vICMSDeson else 0,
        nfe.TotalICMS_vICMSUFDest_Opc if nfe.TotalICMS_vICMSUFDest_Opc else 0,
        nfe.TotalICMS_vICMSUFRemet_Opc if nfe.TotalICMS_vICMSUFRemet_Opc else 0,
        nfe.TotalICMS_vFCPUFDest_Opc if nfe.TotalICMS_vFCPUFDest_Opc else 0,
        nfe.TotalICMS_vFCP if nfe.TotalICMS_vFCP else 0,
        nfe.TotalICMS_vFCPST if nfe.TotalICMS_vFCPST else 0,
        nfe.TotalICMS_vFCPSTRet if nfe.TotalICMS_vFCPSTRet else 0,
        nfe.TotalICMS_vIPIDevol if nfe.TotalICMS_vIPIDevol else 0
    )
    
    ISSQNTot = ''
    retTrib = ''

    return obj_nfe_util.total(ICMSTot, ISSQNTot, retTrib)

def Transp(id_nfe, empresa_filial):
    empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
    nome_tabela = apps.get_model('core', empresa.Tabela)
    nfe = nome_tabela.objects.get(id_nfe=id_nfe)

    if nfe.transp_modFrete == '9':
        mTransporta = ''
    elif nfe.transp_modFrete in('0','1','2'):
        mTransporta = obj_nfe_util.transporta(
            nfe.transporta_CNPJ if nfe.transporta_CNPJ else '',
            nfe.transporta_CPF if nfe.transporta_CPF else '',
            nfe.transporta_xNome.replace('&', '&amp;') if nfe.transporta_xNome else '',
            nfe.transporta_IE if nfe.transporta_IE else '',
            nfe.transporta_xEnder if nfe.transporta_xEnder else '',
            nfe.transporta_xMun if nfe.transporta_xMun else '',
            nfe.transporta_UF if nfe.transporta_UF else ''
        )

    retTransp = ''
    veicTransp = ''
    reboque = ''
    vagao = ''
    balsa = ''
    vol = obj_nfe_util.vol(
        nfe.vol_qVol if nfe.vol_qVol else 0,
        nfe.vol_esp if nfe.vol_esp else '',
        nfe.vol_marca if nfe.vol_marca else '',
        nfe.vol_nVol if nfe.vol_nVol else '',
        nfe.vol_pesoL if nfe.vol_pesoL else 0,
        nfe.vol_pesoB if nfe.vol_pesoB else 0,
        '' # xmlLacres
    )

    return obj_nfe_util.transportador2G(
        nfe.transp_modFrete,
        mTransporta,
        retTransp,
        veicTransp,
        reboque,
        vagao,
        balsa,
        vol
    )

def xmlLocalEntrega(id_nfe, empresa_filial):
    empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
    nome_tabela = apps.get_model('core', empresa.Tabela)
    nfe = nome_tabela.objects.get(id_nfe=id_nfe)

    return obj_nfe_util.localEntregaNT201805(
        nfe.entrega_CNPJ if nfe.entrega_CNPJ else '',
        nfe.entrega_CPF if nfe.entrega_CPF else '',
        nfe.entrega_xNome.replace('&', '&amp;') if nfe.entrega_xNome else '',
        nfe.entrega_xLgr if nfe.entrega_xLgr else '',
        nfe.entrega_nro if nfe.entrega_nro else '',
        nfe.entrega_xCpl if nfe.entrega_xCpl else '',
        nfe.entrega_xBairro if nfe.entrega_xBairro else '',
        nfe.entrega_cMun if nfe.entrega_cMun else '',
        nfe.entrega_xMun if nfe.entrega_xMun else '',
        nfe.entrega_UF if nfe.entrega_UF else '',
        nfe.entrega_CEP if nfe.entrega_CEP else '',
        '',
        '',
        '',
        '',
        ''
    )

def cobr(id_nfe, empresa_filial):
    empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
    nome_tabela = apps.get_model('core', empresa.Tabela)
    nfe = nome_tabela.objects.get(id_nfe=id_nfe)
    cursor = connection.cursor()
    numParc = 1

    if int(nfe.Pedido) < 100000000:
        if isEmpRio(empresa):
            cursor.execute(
                'SELECT Vencimento, Valor_ FROM GreenMotor.dbo.Pagamentos WHERE CodPedido = %s AND Forma = %s AND Conta NOT LIKE %s AND Conta NOT LIKE %s AND Status IS NULL ORDER BY Vencimento',
                [nfe.Pedido, 'BOL', '%-Rio%', 'Ometz%',]
            )
        else:
            cursor.execute(
                'SELECT Vencimento, Valor_ FROM GreenMotor.dbo.Pagamentos WHERE CodPedido = %s AND Forma = %s AND Conta NOT LIKE %s AND Conta NOT LIKE %s AND Status IS NULL ORDER BY Vencimento',
                [nfe.Pedido, 'BOL', '%Rio%', 'Ometz%',]
            )
    else:
        cursor.execute(
            'SELECT Vencimento, Valor_ FROM Lanmax.dbo.Pagamentos WHERE CodPedido = %s AND Forma = %s AND Conta NOT LIKE %s AND Conta NOT LIKE %s AND Status IS NULL ORDER BY Vencimento',
            [nfe.Pedido, 'BOL', '%Rio%', 'Ometz%',]
        )

    rows = cursor.fetchall()
    keys = ('vencimento', 'valor')
    boletos = []

    for row in rows:
        boletos.append(dict(zip(keys, row)))

    mdup = ''

    for bol in boletos:
        mdup += obj_nfe_util.dup(
            f'{numParc:03}',
            bol['vencimento'] if bol['vencimento'] else '',
            bol['valor'] if bol['valor'] else 0
        )

        numParc += 1

    return obj_nfe_util.cobr(
        nfe.cobr_nFat if nfe.cobr_nFat else '',
        nfe.cobr_vOrig if nfe.cobr_vOrig else 0,
        nfe.cobr_vDesc if nfe.cobr_vDesc else 0,
        nfe.cobr_vLiq if nfe.cobr_vLiq else 0,
        mdup
    )

def gera_XMLPagto(id_nfe, empresa_filial):
    empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
    nome_tabela = apps.get_model('core', empresa.Tabela)
    nfe = nome_tabela.objects.get(id_nfe=id_nfe)
    formas_pagto = list(FormasPagto_NFE.objects.filter(id_nfe=id_nfe))
    
    pagto_detPag = ''

    for fp in formas_pagto:
        pagto_detPag += obj_nfe_util.detPag(
            '',
            fp.pagamento_tPag if fp.pagamento_tPag else '',
            fp.pagamento_vPag if fp.pagamento_vPag else 0,
            fp.pagamento_tpIntegra_Opc if fp.pagamento_tpIntegra_Opc else '',
            fp.pagamento_CNPJ_Opc if fp.pagamento_CNPJ_Opc else '',
            fp.pagamento_tBand_Opc if fp.pagamento_tBand_Opc else '',
            fp.pagamento_cAut_Opc if fp.pagamento_cAut_Opc else ''
        )

    return obj_nfe_util.pagamento400(pagto_detPag,nfe.pagamento_vTroco_Opc if nfe.pagamento_vTroco_Opc else 0)

def infAdic(id_nfe, empresa_filial):
    empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
    nome_tabela = apps.get_model('core', empresa.Tabela)
    nfe = nome_tabela.objects.get(id_nfe=id_nfe)

    infAdic_infCpl = nfe.infAdic_infCpl.replace('&', '&amp;') if nfe.infAdic_infCpl else ''
    infAdic_infTrib = nfe.infAdic_infTrib.replace('&', '&amp;') if nfe.infAdic_infTrib else ''
    infAdic_obsCont = ''
    infAdic_obsFisco = ''
    infAdic_procRef = ''

    return obj_nfe_util.infAdic2G(
        nfe.infAdic_infAdFisco.replace('&', '&amp;') if nfe.infAdic_infAdFisco else '',
        infAdic_infCpl + infAdic_infTrib,
        infAdic_obsCont,
        infAdic_obsFisco,
        infAdic_procRef
    )

def dadosIntermed(pedido):
    cursor = connection.cursor()

    if pedido < 100000000:
        cursor.execute(
            'SELECT DISTINCT FormasPagto.CNPJIntermed FROM GreenMotor.dbo.Pagamentos INNER JOIN GreenMotor.dbo.FormasPagto ON Pagamentos.Forma = FormasPagto.Forma WHERE Intermediario = %s AND CodPedido = %s',
            [1, pedido,]
        )
    else:
        cursor.execute(
            'SELECT DISTINCT FormasPagto.CNPJIntermed FROM Lanmax.dbo.Pagamentos INNER JOIN Lanmax.dbo.FormasPagto ON Pagamentos.Forma = FormasPagto.Forma WHERE Intermediario = %s AND CodPedido = %s',
            [1, pedido,]
        )

    result = cursor.fetchone()
    
    if result:
        key = ('cnpj_intermed', )
        intermediario = dict(zip(key, result))
        intermediador = Intermediador.objects.get(CNPJ=intermediario.get('cnpj_intermed'))

        return obj_nfe_util.infIntermed(intermediario.get('cnpj_intermed'), intermediador.idCadIntTran)

    return ''

def consolida_nfe(id_nfe, empresa_filial):
    resultado = ''
    msg_resultado = ''
    empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
    nome_tabela = apps.get_model('core', empresa.Tabela)
    nfe = nome_tabela.objects.get(id_nfe=id_nfe)

    mide = ide(id_nfe, empresa_filial)
    memit = emit(empresa_filial)
    mavulsa = ''
    mdest = dest(id_nfe, empresa_filial)
    mretirada = ''
    mdetalhes = det_prod(id_nfe, empresa_filial)
    mtotal = GTotal_NFe(id_nfe, empresa_filial)
    mtransp = Transp(id_nfe, empresa_filial)

    if nfe.entrega_CEP:
        mentrega = xmlLocalEntrega(id_nfe, empresa_filial)
    else:
        mentrega = ''

    if temBol(id_nfe, empresa_filial) and nfe.Pedido != 0:
        mcobr = cobr(id_nfe, empresa_filial)
    else:
        mcobr = ''

    mpag = gera_XMLPagto(id_nfe, empresa_filial)
    minfadic = infAdic(id_nfe, empresa_filial)
    mexporta = ''
    mcompra = ''
    mcana = ''

    if empresa.emit_UF == 'BA':
        mautxml = obj_nfe_util.autXML('13937073000156', '')
    else:
        mautxml = ''

    if empresa.emit_UF in('AM', 'MT', 'PE', 'PR', 'SC', 'TO'):
        mresptec = obj_nfe_util.infRespTec(
            empresa.emit_CNPJ,
            'Tai Lam',
            'tai@lanmax.com.br',
            '1135666700',
            '',
            '',
            ''
        )
    else:
        mresptec = ''

    if nfe.ide_indIntermed == 1 and nfe.Pedido != 0:
        mintermed = dadosIntermed(int(nfe.Pedido))
    else:
        mintermed = ''

    xml = obj_nfe_util.NFe202006(
        empresa.VersaoSchema,
        nfe.chave_acesso,
        mide,
        memit,
        mavulsa,
        mdest,
        mretirada,
        mentrega,
        mdetalhes,
        mtotal,
        mtransp,
        mcobr,
        mpag,
        minfadic,
        mexporta,
        mcompra,
        mcana,
        mautxml,
        mresptec,
        mintermed
    )

    xml_identado = obj_nfe_util.IdentaXML(xml, resultado, msg_resultado)
    print(xml_identado, resultado, msg_resultado)

    # xml_enviado = Diretorio.objects.filter(CNPJ=empresa.emit_CNPJ, TipoArquivo='xmlEnviado').first()
    destino = os.path.join(settings.BASE_DIR, 'static', 'relatorios')
    xml_enviado = os.path.join(destino, nfe.ide_nNF + '-nfe.xml')
    
    with open(xml_enviado, 'w') as arquivo:
        arquivo.write(xml_identado)
        arquivo.close()