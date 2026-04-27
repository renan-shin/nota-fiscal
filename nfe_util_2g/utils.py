from core.models import *
from lanmax.models import *
from django.apps import apps
from django.db import connection
from django.conf import settings
from pathlib import Path
from datetime import datetime
from pypdf import PdfReader, PdfWriter
from PIL import Image
import win32com.client, os, shutil, base64, qrcode
import xml.etree.ElementTree as ET

try:
    obj_nfe_util = win32com.client.Dispatch("{0162CF2B-365D-4DDE-86F5-F6343110D1A6}")
    print("Objeto COM carregado com sucesso!")
except Exception as e:
    # import traceback
    # traceback.print_exc()
    print(e)

def remove_acentos(texto):
    texto = texto.replace('á','a').replace('Á','A').replace('à','a').replace('À','A').replace('â','a').replace('Â','A').replace('ã','a').replace('Ã','A')
    texto = texto.replace('é','e').replace('É','E').replace('è','e').replace('È','E').replace('ê','e').replace('Ê','E')
    texto = texto.replace('í','i').replace('Í','I').replace('ì','i').replace('Ì','I').replace('î','i').replace('Î','I')
    texto = texto.replace('ó','o').replace('Ó','O').replace('ò','o').replace('Ò','O').replace('ô','o').replace('Ô','O').replace('õ','o').replace('Õ','O')
    texto = texto.replace('ú','u').replace('Ú','U').replace('ù','u').replace('Ù','U').replace('û','u').replace('Û','U')
    texto = texto.replace('ç','c').replace('Ç','C')
    texto = texto.replace('º','o').replace('ª','a')

    return texto

def gera_qrcode(nfe, empresa):
    qr = qrcode.QRCode(
        version=1,                # Tamanho do QR Code (1 é o menor, 40 o maior)
        error_correction=qrcode.constants.ERROR_CORRECT_L, # Nível de correção de erro
        box_size=10,              # Tamanho de cada "quadradinho" em pixels
        border=1,                 # Espessura da borda branca
    )

    qr.add_data(nfe.QRCode)
    qr.make(fit=True)

    diretorio = Diretorio.objects.filter(CNPJ=empresa.emit_CNPJ, TipoArquivo='qrcodes').first()
    arquivo_img = diretorio.Diretorio + nfe.ide_nNF + '.jpg'

    img = qr.make_image(fill_color="black", back_color="white")
    img_final = img.resize((400, 400), resample=Image.NEAREST)
    img_final.save(arquivo_img)

def controleInterno(cod_pedido):
    if cod_pedido < 100000000 and cod_pedido > 0:
        db = 'greenmotor'
    else:
        db = 'lanmax'

    try:
        pedido = Pedido.objects.using(db).get(cod_pedido=cod_pedido)
    except Pedido.DoesNotExist:
        return False
    else:
        if pedido.controle_interno:
            return True
        else:
            return False

def proteger_pdf(arquivo_origem, arquivo_saida, senha_usuario, senha_mestre):
    reader = PdfReader(arquivo_origem)
    writer = PdfWriter()

    for pagina in reader.pages:
        writer.add_page(pagina)

    writer.encrypt(user_password=senha_usuario, owner_password=senha_mestre)

    with open(arquivo_saida, 'wb') as f:
        writer.write(f)

def get_path_repo(nfe, empresa):
    if nfe.ide_mod == 55:
        if nfe.ide_tpNF == 1:
            tipo_arquivo = 'contabilidadeAut'
        else:
            tipo_arquivo = 'repositorio_entrada'
    elif nfe.ide_mod == 65:
        if nfe.ide_tpNF == 1:
            tipo_arquivo = 'repositorio_saidaNFCe'
        else:
            tipo_arquivo = 'repositorio_entradaNFCe'

    pasta_repositorio = Diretorio.objects.filter(CNPJ=empresa.emit_CNPJ, TipoArquivo=tipo_arquivo).first()

    return pasta_repositorio.Diretorio+nfe.ide_dhEmi[:4]+'\\'+nfe.ide_dhEmi[5:7]+'\\'+nfe.ide_nNF+'\\'

def is_suframa(id_nfe, serie):
    cursor = connection.cursor()
    cursor.execute("EXEC Base_NFE.dbo.temSUFRAMA %s,%s", [id_nfe, serie,])
    result = cursor.fetchone()

    if result:
        if result[0] == 1:
            return True
        else:
            return False

    return False

def tem_gnre(id_nfe, serie):
    cursor = connection.cursor()
    cursor.execute("EXEC Base_NFE.dbo.temGNRE %s,%s", [id_nfe, serie,])
    result = cursor.fetchone()

    if result:
        if result[0] == 1:
            return True
        else:
            return False

    return False

def gera_difal(id_nfe, serie):
    cursor = connection.cursor()
    cursor.execute("EXEC Base_NFE.dbo.geraDIFAL %s,%s", [id_nfe, serie,])
    result = cursor.fetchone()

    if result:
        if result[0] == 1:
            return True
        else:
            return False
    
    return False

def tem_difal(id_nfe, serie):
    cursor = connection.cursor()
    cursor.execute("EXEC Base_NFE.dbo.temDIFAL %s,%s", [id_nfe, serie,])
    result = cursor.fetchone()

    if result:
        if result[0] == 1:
            return True
        else:
            return False
    
    return False

def gera_fcp(id_nfe, serie):
    cursor = connection.cursor()
    cursor.execute("EXEC Base_NFE.dbo.geraFCP %s,%s", [id_nfe, serie,])
    result = cursor.fetchone()

    if result:
        if result[0] == 1:
            return True
        else:
            return False
    
    return False
    

def isEmpRio(empresa):
    if empresa.ide_serie in(8, 81, 82, 83, 84, 85):
        return True

    return False

def semNCob(nfe, empresa):
    cursor = connection.cursor()

    if int(nfe.Pedido) < 100000000:
        cursor.execute("SELECT * FROM GreenMotor.dbo.Pagamentos WHERE CodPedido = %s AND Forma = %s AND NCob IS NULL", [nfe.Pedido, 'BOL',])
    else:
        cursor.execute("SELECT * FROM Lanmax.dbo.Pagamentos WHERE CodPedido = %s AND Forma = %s AND NCob IS NULL", [nfe.Pedido, 'BOL',])

    rows = cursor.fetchall()
    
    if len(rows) > 0:
        return True

    return False

def temBolSemRio(nfe, empresa):
    cursor = connection.cursor()

    if int(nfe.Pedido) < 100000000 and int(nfe.Pedido) > 0:
        cursor.execute("SELECT * FROM GreenMotor.dbo.Pagamentos WHERE CodPedido = %s AND Forma = %s AND Conta NOT LIKE %s AND Conta NOT LIKE %s", [nfe.Pedido, 'BOL', '%Rio%', 'Ometz%',])
    else:
        cursor.execute("SELECT * FROM Lanmax.dbo.Pagamentos WHERE CodPedido = %s AND Forma = %s AND Conta NOT LIKE %s AND Conta NOT LIKE %s", [nfe.Pedido, 'BOL', '%Rio%', 'Ometz%',])

    rows = cursor.fetchall()
    
    if len(rows) > 0:
        return True

    return False

def temBol(nfe, empresa):
    cursor = connection.cursor()

    if int(nfe.Pedido) < 100000000 and int(nfe.Pedido) > 0:
        cursor.execute("SELECT * FROM GreenMotor.dbo.Pagamentos WHERE CodPedido = %s AND Forma = %s", [nfe.Pedido, 'BOL',])
    else:
        cursor.execute("SELECT * FROM Lanmax.dbo.Pagamentos WHERE CodPedido = %s AND Forma = %s AND Conta NOT LIKE %s", [nfe.Pedido, 'BOL', 'Ometz%',])

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

def ide(nfe, empresa):
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

    compraGov_tpEnteGov = nfe.compraGov_tpEnteGov if nfe.compraGov_tpEnteGov else 0

    if compraGov_tpEnteGov > 0:
        gCompraGov_Opc = CompraGov(nfe)
    else:
        gCompraGov_Opc = ''

    if nfe.NFAntePgto_chaveNFe:
        gPagAntecipado_Opc = NFAntePgto_RefNF(nfe)
    else:
        gPagAntecipado_Opc = ''
    
    return obj_nfe_util.identificadorRTCv130(
        # nfe.ide_cUF if nfe.ide_cUF else 0,
        empresa.emit_cUF,
        int(nfe.ide_cNF) if nfe.ide_cNF is not None else 0,
        nfe.ide_natOp if nfe.ide_natOp else '',
        int(nfe.ide_mod) if nfe.ide_mod is not None else 55,
        nfe.ide_serie if nfe.ide_serie else 0,
        nfe.ide_nNF if nfe.ide_nNF else '0',
        nfe.ide_dhEmi if nfe.ide_dhEmi else '',
        nfe.ide_dhSaiEnt if nfe.ide_dhSaiEnt else '',
        int(nfe.ide_tpNF) if nfe.ide_tpNF is not None else 1,
        int(nfe.ide_idDest) if nfe.ide_idDest is not None else 1,
        empresa.emit_cMun if empresa.emit_cMun else '',
        ide_nfref.replace(' ', ''),
        int(nfe.ide_tpImp) if nfe.ide_tpImp is not None else 1,
        int(nfe.ide_tpEmis) if nfe.ide_tpEmis is not None else 1,
        int(nfe.ide_cDV) if nfe.ide_cDV is not None else 0,
        int(nfe.ide_tpAmb) if nfe.ide_tpAmb is not None else 1,
        int(nfe.ide_finNFe) if nfe.ide_finNFe is not None else 1,
        int(nfe.ide_indFinal) if nfe.ide_indFinal is not None else 0,
        int(nfe.ide_indPres) if nfe.ide_indPres is not None else 0,
        int(nfe.ide_procEmi) if nfe.ide_procEmi is not None else 0,
        nfe.ide_verProc if nfe.ide_verProc else '',
        nfe.ide_dhCont if nfe.ide_dhCont else '',
        nfe.ide_xJust if nfe.ide_xJust else '',
        int(nfe.ide_indIntermed) if nfe.ide_indIntermed is not None else 0,
        nfe.ide_cMunFGIBS_Opc if nfe.ide_cMunFGIBS_Opc else '',
        nfe.ide_tpNFDebito_Opc if nfe.ide_tpNFDebito_Opc else '',
        nfe.ide_tpNFCredito_Opc if nfe.ide_tpNFCredito_Opc else '',
        gCompraGov_Opc,
        gPagAntecipado_Opc,
        nfe.ide_dPrevEntrega_Opc if nfe.ide_dPrevEntrega_Opc else ''
    )

def emit(empresa):
    return obj_nfe_util.emitente2G(
        empresa.emit_CNPJ,
        '',# empresa.emit_CPF,
        empresa.emit_xNome,
        empresa.emit_xFant if empresa.emit_xFant else '',
        empresa.emit_xLgr,
        empresa.emit_nro,
        empresa.emit_xCpl if empresa.emit_xCpl else '',
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

def dest(nfe, empresa):
    if nfe.sTP == 1:
        dest_CPF = nfe.dest_CPF
        dest_CNPJ = ''
    elif nfe.sTP == 2:
        dest_CNPJ = nfe.dest_CNPJ
        dest_CPF = ''

    if int(nfe.dest_indIEDest) == 1:
        dest_IE = nfe.dest_IE
    elif int(nfe.dest_indIEDest) in(2,9):
        dest_IE = ''

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
        dest_IE,
        nfe.dest_ISUF if nfe.dest_ISUF else '',
        nfe.dest_IM if nfe.dest_IM else '',
        nfe.dest_eMail if nfe.dest_eMail else ''
    )

def det_prod(nfe, nfe_itens, empresa):
    produtos = ''

    for item in nfe_itens:
        det_infAdprod = ''
        prod_di = ''

        if not item.det_infAdprod:
            det_infAdprod = item.NumSerie if item.NumSerie else ''
        else:
            det_infAdprod += '|' + item.NumSerie if item.NumSerie else ''

        if int(item.prod_CFOP) >= 3101 and int(item.prod_CFOP) <= 3999:
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

        if item.cCredPresumido:
            credPresumido_Opc = CredPresumido(item)
        else:
            credPresumido_Opc = ''

        det_produto = obj_nfe_util.produtoRTCv130(
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
            int(item.prod_qCOM) if item.prod_qCOM else 0,
            round(item.prod_vUnCOM, 10) if item.prod_vUnCOM else 0,
            item.prod_vProd if item.prod_vProd else 0,
            item.prod_cEANTrib if item.prod_cEANTrib else '',
            item.prod_uTrib if item.prod_uTrib else 0,
            int(item.prod_qTrib) if item.prod_qTrib else 0,
            round(item.prod_vUnTrib, 10) if item.prod_vUnTrib else 0,
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
            '', # rastro
            credPresumido_Opc,
            item.indBemMovelUsado_Opc if item.indBemMovelUsado_Opc else 0,
            item.tpCredPresIBSZFM_Opc if item.tpCredPresIBSZFM_Opc else ''
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

        if tem_difal(nfe.id_nfe, empresa.ide_serie) and empresa.emit_CRT == 3:
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
        
        if nfe.ide_mod == 55:
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
        else:
            det_IPI = ''

        if int(item.prod_CFOP) >= 3101 and int(item.prod_CFOP) <= 3999:
            det_II = obj_nfe_util.II(
                item.II_vBC if item.II_vBC else 0,
                item.II_vDespAdu if item.II_vDespAdu else 0,
                item.II_vII if item.II_vII else 0,
                item.II_vIOF if item.II_vIOF else 0
            )
        else:
            det_II = ''

        det_PISST = ''
        det_COFINSST = ''
        det_ISSQN = ''

        det_IS = '' # gera_IS(id_nfe, id_item)

        if empresa.emit_CRT == 2 or empresa.emit_CRT == 3:
            det_IBSCBS = gera_IBSCBS(nfe, empresa, item)
        else:
            det_IBSCBS = ''

        det_imposto = obj_nfe_util.impostoRTC(
            item.imp_vTotTrib if item.imp_vTotTrib else 0,
            det_ICMS,
            det_IPI,
            det_II,
            det_PIS,
            det_COFINS,
            det_PISST,
            det_COFINSST,
            det_ISSQN,
            det_ICMSUFDest,
            det_IS,
            det_IBSCBS
        )

        det_obsContItem = obj_nfe_util.obsCont('', '')
        det_obsFiscoItem = obj_nfe_util.obsCont('', '')

        if item.chaveAcessoRef:
            det_DFeReferenciado = DFeReferenciado(item)
        else:
            det_DFeReferenciado = ''

        produtos += obj_nfe_util.detalheRTC(
            item.det_nItem if item.det_nItem else 0,
            det_produto,
            det_imposto,
            det_infAdprod,
            item.det_pDevol_Opc if item.det_pDevol_Opc else 0,
            item.det_vIPIDevol_Opc if item.det_vIPIDevol_Opc else 0,
            det_obsContItem,
            det_obsFiscoItem,
            item.det_vItem if item.det_vItem else 0,
            det_DFeReferenciado
        )

    return produtos

def CompraGov(nfe):
    return obj_nfe_util.gCompraGov(
        nfe.compraGov_tpEnteGov,
        nfe.compraGov_pRedutor if nfe.compraGov_pRedutor else 0,
        nfe.compraGov_tpOperGov
    )

def NFAntePgto_RefNF(nfe):
    chaves = nfe.NFAntePgto_chaveNFe
    xml = ''

    for chave in chaves:
        xml = obj_nfe_util.refNFe(chave) + xml

    return xml.replace(' ', '')

def gera_IBSCBS(nfe, empresa, item):
    if item.IBSCBS_CST == '000' or item.IBSCBS_CST == '200' or item.IBSCBS_CST == '510' or item.IBSCBS_CST == '515' or item.IBSCBS_CST == '550':
        gTributo = gIBSCBS(nfe, empresa.ide_serie, item)
    elif item.IBSCBS_CST == '620':
        gTributo = gIBSCBSMono(item)
    elif item.IBSCBS_CST == '800':
        gTributo = gTransfCred(item)
    elif item.IBSCBS_CST == '811':
        gTributo = gAjusteCompet(item)
    elif item.IBSCBS_CST == '410' or item.IBSCBS_CST == '810' or item.IBSCBS_CST == '830':
        gTributo = ''
    else:
        gTributo = ''

    gEstornoCred_vCBSEstCred = item.gEstornoCred_vCBSEstCred if item.gEstornoCred_vCBSEstCred else 0
    gCredPresIBSZFM_vCredPresIBSZFM = item.gCredPresIBSZFM_vCredPresIBSZFM if item.gCredPresIBSZFM_vCredPresIBSZFM else 0

    if item.IBSCBS_CST == '811' and gEstornoCred_vCBSEstCred > 0:
        gEstornoCred_Opc = gEstornoCred(item)
    else:
        gEstornoCred_Opc = ''

    if item.IBSCBS_CST == '810' and gCredPresIBSZFM_vCredPresIBSZFM > 0:
        gCredPresumido_Opc = gCredPresIBSZFM(item)
    else:
        gCredPresumido_Opc = ''

    return obj_nfe_util.IBSCBSv130(
        item.IBSCBS_CST,
        item.IBSCBS_cClassTrib,
        item.IBSCBS_indDoacao_Opc if item.IBSCBS_indDoacao_Opc else '',
        gTributo,
        gEstornoCred_Opc,
        gCredPresumido_Opc
    )

def gIBSCBS(nfe, serie, item):
    if is_suframa(nfe.id_nfe, serie):
        gTribRegular_Opc = gTribRegular(item)
    else:
        gTribRegular_Opc = ''

    compraGov_tpEnteGov = nfe.compraGov_tpEnteGov if nfe.compraGov_tpEnteGov else 0

    if compraGov_tpEnteGov > 0:
        gTribCompraGov_Opc = gTribCompraGov(item)
    else:
        gTribCompraGov_Opc = ''

    grupoIBSUF = gIBSUF(item)
    grupoIBSMun = gIBSMun(item)
    grupoCBS = gCBS(item)

    return obj_nfe_util.gIBSCBSv130(
        item.IBSCBS_vBC if item.IBSCBS_vBC else 0,
        grupoIBSUF,
        grupoIBSMun,
        item.IBSCBS_vIBS if item.IBSCBS_vIBS else 0,
        grupoCBS,
        gTribRegular_Opc,
        gTribCompraGov_Opc
    )

def gIBSCBSMono(item):
    return obj_nfe_util.gIBSCBSMono(
        item.gIBSCBSMono_qBCMono_Opc if item.gIBSCBSMono_qBCMono_Opc else 0,
        item.gIBSCBSMono_adRemIBS_Opc if item.gIBSCBSMono_adRemIBS_Opc else 0,
        item.gIBSCBSMono_adRemCBS_Opc if item.gIBSCBSMono_adRemCBS_Opc else 0,
        item.gIBSCBSMono_vIBSMono_Opc if item.gIBSCBSMono_vIBSMono_Opc else 0,
        item.gIBSCBSMono_vCBSMono_Opc if item.gIBSCBSMono_vCBSMono_Opc else 0,
        item.gIBSCBSMono_qBCMonoReten_Opc if item.gIBSCBSMono_qBCMonoReten_Opc else 0,
        item.gIBSCBSMono_adRemIBSReten_Opc if item.gIBSCBSMono_adRemIBSReten_Opc else 0,
        item.gIBSCBSMono_vIBSMonoReten_Opc if item.gIBSCBSMono_vIBSMonoReten_Opc else 0,
        item.gIBSCBSMono_adRemCBSReten_Opc if item.gIBSCBSMono_adRemCBSReten_Opc else 0,
        item.gIBSCBSMono_vCBSMonoReten_Opc if item.gIBSCBSMono_vCBSMonoReten_Opc else 0,
        item.gIBSCBSMono_qBCMonoRet_Opc if item.gIBSCBSMono_qBCMonoRet_Opc else 0,
        item.gIBSCBSMono_adRemIBSRet_Opc if item.gIBSCBSMono_adRemIBSRet_Opc else 0,
        item.gIBSCBSMono_vIBSMonoRet_Opc if item.gIBSCBSMono_vIBSMonoRet_Opc else 0,
        item.gIBSCBSMono_adRemCBSRet_Opc if item.gIBSCBSMono_adRemCBSRet_Opc else 0,
        item.gIBSCBSMono_vCBSMonoRet_Opc if item.gIBSCBSMono_vCBSMonoRet_Opc else 0,
        item.gIBSCBSMono_pDifIBS_Opc if item.gIBSCBSMono_pDifIBS_Opc else 0,
        item.gIBSCBSMono_vIBSMonoDif_Opc if item.gIBSCBSMono_vIBSMonoDif_Opc else 0,
        item.gIBSCBSMono_pDifCBS_Opc if item.gIBSCBSMono_pDifCBS_Opc else 0,
        item.gIBSCBSMono_vCBSMonoDif_Opc if item.gIBSCBSMono_vCBSMonoDif_Opc else 0,
        item.gIBSCBSMono_vTotIBSMonoItem if item.gIBSCBSMono_vTotIBSMonoItem else 0,
        item.gIBSCBSMono_vTotCBSMonoItem if item.gIBSCBSMono_vTotCBSMonoItem else 0
    )

def gTransfCred(item):
    return obj_nfe_util.gTransfCred(
        item.gTransfCred_vIBS if item.gTransfCred_vIBS else 0,
        item.gTransfCred_vCBS if item.gTransfCred_vCBS else 0
    )

def gAjusteCompet(item):
    return obj_nfe_util.gAjusteCompet(
        item.gAjusteCompet_competApur,
        item.gAjusteCompet_vIBS if item.gAjusteCompet_vIBS else 0,
        item.gAjusteCompet_vCBS if item.gAjusteCompet_vCBS else 0
    )

def gEstornoCred(item):
    return obj_nfe_util.gEstornoCred(
        item.gEstornoCred_vIBSEstCred if item.gEstornoCred_vIBSEstCred else 0,
        item.gEstornoCred_vCBSEstCred if item.gEstornoCred_vCBSEstCred else 0
    )

def gCredPresIBSZFM(item):
    return obj_nfe_util.gCredPresIBSZFMv130(
        item.gCredPresIBSZFM_competApur,
        item.gCredPresIBSZFM_tpCredPresIBSZFM if item.gCredPresIBSZFM_tpCredPresIBSZFM else '',
        item.gCredPresIBSZFM_vCredPresIBSZFM if item.gCredPresIBSZFM_vCredPresIBSZFM else 0
    )

def DFeReferenciado(item):
    return obj_nfe_util.DFeReferenciado(
        item.chaveAcessoRef,
        item.det_nItem if item.det_nItem else 0
    )

def CredPresumido(item):
    return obj_nfe_util.CredPresumido(
        item.cCredPresumido,
        item.pCredPresumido if item.pCredPresumido else 0,
        item.vCredPresumido if item.vCredPresumido else 0
    )

def gIBSUF(item):
    return obj_nfe_util.gIBSUF(
        item.gIBSUF_pIBSUF if item.gIBSUF_pIBSUF else 0,
        item.gIBSUF_pDif_Opc if item.gIBSUF_pDif_Opc else 0,
        item.gIBSUF_vDif_Opc if item.gIBSUF_vDif_Opc else 0,
        item.gIBSUF_vDevTrib_Opc if item.gIBSUF_vDevTrib_Opc else 0,
        item.gIBSUF_pRedAliq_Opc if item.gIBSUF_pRedAliq_Opc else 0,
        item.gIBSUF_pAliqEfet_Opc if item.gIBSUF_pAliqEfet_Opc else 0,
        item.gIBSUF_vIBSUF if item.gIBSUF_vIBSUF else 0
    )

def gIBSMun(item):
    return obj_nfe_util.gIBSMun(
        item.gIBSMun_pIBSMun if item.gIBSMun_pIBSMun else 0,
        item.gIBSMun_pDif_Opc if item.gIBSMun_pDif_Opc else 0,
        item.gIBSMun_vDif_Opc if item.gIBSMun_vDif_Opc else 0,
        item.gIBSMun_vDevTrib_Opc if item.gIBSMun_vDevTrib_Opc else 0,
        item.gIBSMun_pRedAliq_Opc if item.gIBSMun_pRedAliq_Opc else 0,
        item.gIBSMun_pAliqEfet_Opc if item.gIBSMun_pAliqEfet_Opc else 0,
        item.gIBSMun_vIBSMun if item.gIBSMun_vIBSMun else 0
    )

def gCBS(item):
    return obj_nfe_util.gCBS(
        item.gCBS_pCBS if item.gCBS_pCBS else 0,
        item.gCBS_pDif_Opc if item.gCBS_pDif_Opc else 0,
        item.gCBS_vDif_Opc if item.gCBS_vDif_Opc else 0,
        item.gCBS_vDevTrib_Opc if item.gCBS_vDevTrib_Opc else 0,
        item.gCBS_pRedAliq_Opc if item.gCBS_pRedAliq_Opc else 0,
        item.gCBS_pAliqEfet_Opc if item.gCBS_pAliqEfet_Opc else 0,
        item.gCBS_vCBS if item.gCBS_vCBS else 0
    )

def gTribRegular(item):
    return obj_nfe_util.gTribRegular(
        item.gTribRegular_CSTReg,
        item.gTribRegular_cClassTribReg,
        item.gTribRegular_pAliqEfetRegIBSUF if item.gTribRegular_pAliqEfetRegIBSUF else 0,
        item.gTribRegular_vTribRegIBSUF if item.gTribRegular_vTribRegIBSUF else 0,
        item.gTribRegular_pAliqEfetRegIBSMun if item.gTribRegular_pAliqEfetRegIBSMun else 0,
        item.gTribRegular_vTribRegIBSMun if item.gTribRegular_vTribRegIBSMun else 0,
        item.gTribRegular_pAliqEfetRegCBS if item.gTribRegular_pAliqEfetRegCBS else 0,
        item.gTribRegular_vTribRegCBS if item.gTribRegular_vTribRegCBS else 0
    )

def gTribCompraGov(item):
    return obj_nfe_util.gTribCompraGov(
        item.gTribCompraGov_pAliqIBSUF if item.gTribCompraGov_pAliqIBSUF else 0,
        item.gTribCompraGov_vTribIBSUF if item.gTribCompraGov_vTribIBSUF else 0,
        item.gTribCompraGov_pAliqIBSMun if item.gTribCompraGov_pAliqIBSMun else 0,
        item.gTribCompraGov_vTribIBSMun if item.gTribCompraGov_vTribIBSMun else 0,
        item.gTribCompraGov_pAliqCBS if item.gTribCompraGov_pAliqCBS else 0,
        item.gTribCompraGov_vTribCBS if item.gTribCompraGov_vTribCBS else 0
    )

def GTotal_NFe(nfe, empresa):
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

    if empresa.emit_CRT == 2 or empresa.emit_CRT == 3:
        IBSCBSTot = TotalIBSCBS(nfe)
    else:
        IBSCBSTot = ''

    return obj_nfe_util.totalRTC(
        ICMSTot,
        ISSQNTot,
        retTrib,
        nfe.totalRTC_vIS if nfe.totalRTC_vIS else 0,
        IBSCBSTot,
        nfe.totalRTC_vNFTot if nfe.totalRTC_vNFTot else 0.001
    )

def TotalIBSCBS(nfe):
    gIBS_Opc = TotalIBS(nfe)
    gCBS_Opc = TotalCBS(nfe)
    gMono_Opc = TotalMono(nfe)
    gEstornoCred_Opc = TotalEstornoCred(nfe)

    return obj_nfe_util.IBSCBSTotv130(
        nfe.IBSCBSTot_vBCIBSCBS if nfe.IBSCBSTot_vBCIBSCBS else 0,
        gIBS_Opc,
        gCBS_Opc,
        gMono_Opc,
        gEstornoCred_Opc
    )

def TotalIBS(nfe):
    return obj_nfe_util.gIBSTot(
        nfe.IBSTot_vDif_UF if nfe.IBSTot_vDif_UF else 0,
        nfe.IBSTot_vDevTrib_UF if nfe.IBSTot_vDevTrib_UF else 0,
        nfe.IBSTot_vIBS_UF if nfe.IBSTot_vIBS_UF else 0,
        nfe.IBSTot_vDif_Mun if nfe.IBSTot_vDif_Mun else 0,
        nfe.IBSTot_vDevTrib_Mun if nfe.IBSTot_vDevTrib_Mun else 0,
        nfe.IBSTot_vIBS_Mun if nfe.IBSTot_vIBS_Mun else 0,
        nfe.IBSTot_vIBS if nfe.IBSTot_vIBS else 0,
        nfe.IBSTot_vCredPres if nfe.IBSTot_vCredPres else 0,
        nfe.IBSTot_vCredPresCondSus if nfe.IBSTot_vCredPresCondSus else 0
    )

def TotalCBS(nfe):
    return obj_nfe_util.gCBSTot(
        nfe.CBSTot_vDif if nfe.CBSTot_vDif else 0,
        nfe.CBSTot_vDevTrib if nfe.CBSTot_vDevTrib else 0,
        nfe.CBSTot_vCBS if nfe.CBSTot_vCBS else 0,
        nfe.CBSTot_vCredPres if nfe.CBSTot_vCredPres else 0,
        nfe.CBSTot_vCredPresCondSus if nfe.CBSTot_vCredPresCondSus else 0
    )

def TotalMono(nfe):
    return obj_nfe_util.gMonoTot(
        nfe.MonoTot_vIBSMono if nfe.MonoTot_vIBSMono else 0,
        nfe.MonoTot_vCBSMono if nfe.MonoTot_vCBSMono else 0,
        nfe.MonoTot_vIBSMonoReten if nfe.MonoTot_vIBSMonoReten else 0,
        nfe.MonoTot_vCBSMonoReten if nfe.MonoTot_vCBSMonoReten else 0,
        nfe.MonoTot_vIBSMonoRet if nfe.MonoTot_vIBSMonoRet else 0,
        nfe.MonoTot_vCBSMonoRet if nfe.MonoTot_vCBSMonoRet else 0
    )

def TotalEstornoCred(nfe):
    return obj_nfe_util.gEstornoCred(
        nfe.EstornoCred_vIBSEstCred if nfe.EstornoCred_vIBSEstCred else 0,
        nfe.EstornoCred_vCBSEstCred if nfe.EstornoCred_vCBSEstCred else 0
    )

def Transp(nfe):
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

def exporta(nfe, empresa):
    return obj_nfe_util.exporta310(
        nfe.exporta_UFSaidaPais if nfe.exporta_UFSaidaPais else '',
        nfe.exporta_xLocEmbarq if nfe.exporta_xLocEmbarq else '',
        nfe.exporta_xLocDespacho_Opc if nfe.exporta_xLocDespacho_Opc else ''
    )

def xmlLocalEntrega(nfe, empresa):
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

def cobr(nfe, empresa):
    cursor = connection.cursor()
    numParc = 1

    if int(nfe.Pedido) < 100000000:
        if isEmpRio(empresa):
            conta = '%-Rio%'
        else:
            conta = '%Rio%'

        cursor.execute(
            'SELECT Vencimento, Valor_ FROM GreenMotor.dbo.Pagamentos WHERE CodPedido = %s AND Forma = %s AND Conta NOT LIKE %s AND Conta NOT LIKE %s AND Status IS NULL ORDER BY Vencimento',
            [nfe.Pedido, 'BOL', conta, 'Ometz%',]
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

def gera_XMLPagto(nfe, empresa):
    formas_pagto = list(FormasPagto_NFE.objects.filter(id_nfe=nfe.id_nfe, ide_serie=empresa.ide_serie))
    
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

def infAdic(nfe, empresa):
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

def gera_chave_acesso(nfe, empresa):
    hoje = datetime.now()
    ano = hoje.strftime('%y')
    mes = hoje.strftime('%m')
    status = 0
    msg_resultado = ''
    cnf = ''
    cdv = ''
    chave_nfe = ''
    vhv = ''

    resultado = obj_nfe_util.CriaChaveNFe2G(
        empresa.emit_cUF,
        ano,
        mes,
        empresa.emit_CNPJ,
        int(nfe.ide_mod),
        empresa.ide_serie,
        nfe.ide_nNF,
        int(nfe.ide_tpEmis),
        empresa.ChaveSeguranca,
        msg_resultado,
        cnf,
        cdv,
        chave_nfe
    )

    status, msg_resultado, cnf, cdv, chave_nfe = resultado

    if status == 5601:
        if empresa.sHV == 0:
            vhv = '-03:00'
        elif empresa.sHV == 1:
            vhv = '-02:00'

        nfe.chave_acesso = chave_nfe
        nfe.ide_cNF = cnf
        nfe.ide_cDV = cdv
        nfe.ide_dhEmi = hoje.strftime('%Y-%m-%d') + 'T' + hoje.strftime('%H:%M:%S') + vhv
        nfe.save()

    return status

def gera_xml(nfe, nfe_itens, empresa):
    resultado = ''
    msg_resultado = ''

    mide = ide(nfe, empresa)
    memit = emit(empresa)

    mavulsa = ''

    if nfe.ide_mod == 55:
        mdest = dest(nfe, empresa)
    elif nfe.ide_mod == 65:
        if nfe.ECFRef_mod and nfe.ECFRef_mod == 1:
            mdest = dest(nfe, empresa)
        else:
            mdest = ''
    else:
        mdest = ''

    mretirada = ''
    mdetalhes = det_prod(nfe, nfe_itens, empresa)
    mtotal = GTotal_NFe(nfe, empresa)
    mtransp = Transp(nfe)

    if nfe.entrega_CEP:
        mentrega = xmlLocalEntrega(nfe, empresa)
    else:
        mentrega = ''

    if (isEmpRio(empresa) and temBol(nfe, empresa)) or temBolSemRio(nfe, empresa):
        mcobr = cobr(nfe, empresa)
    else:
        mcobr = ''


    mpag = gera_XMLPagto(nfe, empresa)
    minfadic = infAdic(nfe, empresa)

    if int(nfe.ide_idDest) == 3 and int(nfe.ide_tpNF) == 1:
        mexporta = exporta(nfe, empresa)
    else:
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

    if nfe.ide_mod == 55:
        tipo_arquivo = 'xmlEnviado'
    elif nfe.ide_mod == 65:
        tipo_arquivo = 'xmlEnviadoNFCe'
    else:
        tipo_arquivo = ''

    xml_enviado = Diretorio.objects.filter(CNPJ=empresa.emit_CNPJ, TipoArquivo=tipo_arquivo).first()

    if Path(xml_enviado.Diretorio).is_dir():
        with open(xml_enviado.Diretorio + nfe.ide_nNF + '-nfe.xml', 'w', encoding='utf-8') as arquivo:
            arquivo.write(xml)
            arquivo.close()

def assina_nfce(nfe, empresa):
    diretorio = Diretorio.objects.filter(CNPJ=empresa.emit_CNPJ, TipoArquivo='xmlEnviadoNFCe').first()
    caminho_xml = diretorio.Diretorio + nfe.ide_nNF + '-nfe.xml'

    with open(caminho_xml, "r", encoding="utf-8") as f:
        xml = f.read()

    versao_qrcode = '2'
    ind_sinc = '1'
    resultado = 0
    msg_resultado = ''
    lote = ''
    url_nfce = ''
    status = 0
    xml_assinado = ''

    retorno = obj_nfe_util.AssinarNFCe400(
        xml,
        empresa.Certificado,
        empresa.idTokenNFCe,
        empresa.CodSegNFCe,
        versao_qrcode,
        empresa.URLNFCe,
        empresa.URLChave,
        ind_sinc,
        resultado,
        msg_resultado,
        lote,
        url_nfce
    )

    xml, status, msg_resultado, xml_assinado, url_nfce = retorno
    
    if status == 5300:
        nfe.status_sefaz = 'Lote recebido com sucesso'
        nfe.QRCode = url_nfce
        nfe.save()
        nfe.refresh_from_db()

        diretorio = Diretorio.objects.filter(CNPJ=empresa.emit_CNPJ, TipoArquivo='xmlAssinadoNFCe').first()
        caminho_xml = diretorio.Diretorio + nfe.ide_nNF + '-nfeAssinado.xml'

        if Path(diretorio.Diretorio).is_dir():
            with open(caminho_xml, 'w', encoding='utf-8') as arquivo:
                arquivo.write(xml)
                arquivo.close()

        pasta_repo_nfe = get_path_repo(nfe, empresa)

        if not Path(pasta_repo_nfe).is_dir():
            Path(pasta_repo_nfe).mkdir(parents=True, exist_ok=True)

        shutil.copy(caminho_xml, pasta_repo_nfe)

def envia_nfe_sincrono(nfe, empresa):
    if nfe.ide_mod == 55:
        xml_enviado = Diretorio.objects.filter(CNPJ=empresa.emit_CNPJ, TipoArquivo='xmlEnviado').first()
        arquivo_xml = xml_enviado.Diretorio + nfe.ide_nNF + '-nfe.xml'
    elif nfe.ide_mod == 65:
        xml_enviado = Diretorio.objects.filter(CNPJ=empresa.emit_CNPJ, TipoArquivo='xmlAssinadoNFCe').first()
        arquivo_xml = xml_enviado.Diretorio + nfe.ide_nNF + '-nfeAssinado.xml'

    with open(arquivo_xml, "r", encoding="utf-8") as f:
        xml = f.read()

    msg_dados = ''
    msg_ret_ws = ''
    cstat = 0
    msg_resultado = ''
    nro_protocolo = ''
    dh_protocolo = ''
    nfe_assinada = ''

    if nfe.ide_mod == 55:
        sigla_webservice = empresa.SiglaWebService.upper()
    elif nfe.ide_mod == 65:
        sigla_webservice = empresa.SiglaWebService.lower()

    retorno = obj_nfe_util.EnviaNFSincrono(
        sigla_webservice,
        xml,
        empresa.Certificado,
        empresa.VersaoSchema,
        msg_dados,
        msg_ret_ws,
        cstat,
        msg_resultado,
        nro_protocolo,
        dh_protocolo,
        nfe_assinada,
        '',
        '',
        '',
        empresa.LicencaDLL
    )

    xml_retorno, msg_dados, msg_ret_ws, cstat, msg_resultado, nro_protocolo, dh_protocolo, nfe_assinada = retorno

    if cstat == 100:
        if nfe.ide_mod == 55:
            nfe.ECFRef_mod = 2
        nfe.Transmitir = False
        nfe.save()
        nfe.refresh_from_db()

        if nfe.ide_mod == 55:
            tipo_arquivo_autorizado = 'xmlAutorizado'
            tipo_arquivo_enviado = 'xmlEnviado'
        elif nfe.ide_mod == 65:
            tipo_arquivo_autorizado = 'xmlAutorizadoNFCe'
            tipo_arquivo_enviado = 'xmlEnviadoNFCe'

        pasta_autorizado = Diretorio.objects.filter(CNPJ=empresa.emit_CNPJ, TipoArquivo=tipo_arquivo_autorizado).first()
        xml_autorizado = pasta_autorizado.Diretorio + nfe.ide_nNF + '-procNFe.xml'
        pasta_enviado = Diretorio.objects.filter(CNPJ=empresa.emit_CNPJ, TipoArquivo=tipo_arquivo_enviado).first()
        xml_enviado = pasta_enviado.Diretorio + nfe.ide_nNF + '-nfe.xml'
        
        if Path(pasta_autorizado.Diretorio).is_dir():
            with open(xml_autorizado, 'w', encoding='utf-8') as arquivo:
                arquivo.write(xml_retorno)
                arquivo.close()

            cursor = connection.cursor()

            cursor.execute("SELECT TOP 1 usuario FROM NFe_Auditoria_400 WHERE pedido = %s AND NF = %s AND Status = %s AND usuario <> %s ORDER BY data_historico DESC", [nfe.Pedido, nfe.ide_nNF, 'NFe não enviada', 'sa'])
            result = cursor.fetchone()

            cursor.execute("EXEC AS LOGIN=%s; EXEC acertaNFe %s, %s", [result[0], pasta_autorizado.Diretorio, nfe.ide_nNF + '-procNFe.xml'])

            if int(nfe.Pedido) < 100000000 and int(nfe.Pedido) > 0:
                cursor.execute("EXEC AS LOGIN=%s; EXEC GreenMotor.dbo.Pedido_07Fatura %s, %s", [result[0], nfe.Pedido, nfe.ide_nNF])
            elif int(nfe.Pedido) >= 100000000:
                if int(nfe.ide_mod) == 65:
                    cursor.execute("EXEC AS LOGIN=%s; EXEC Lanmax.dbo.Pedido_07Fatura %s, %s, %s", [result[0], nfe.Pedido, nfe.ide_nNF, 65])
                elif int(nfe.ide_mod) == 55:
                    cursor.execute("EXEC AS LOGIN=%s; EXEC Lanmax.dbo.Pedido_07Fatura %s, %s", [result[0], nfe.Pedido, nfe.ide_nNF])

            cursor.execute('REVERT;')

            nfe.refresh_from_db()

            if semNCob(nfe, empresa):
                if int(nfe.Pedido) < 100000000 and int(nfe.Pedido) > 0:
                    cursor.execute('EXEC geraNossoNumero_GM %s', [nfe.Pedido,])
                else:
                    cursor.execute('EXEC geraNossoNumero %s', [nfe.Pedido,])

            if Path(xml_autorizado).is_file():
                pasta_repo_nfe = get_path_repo(nfe, empresa)

                if not Path(pasta_repo_nfe).is_dir():
                    Path(pasta_repo_nfe).mkdir(parents=True, exist_ok=True)

                shutil.copy(xml_autorizado, pasta_repo_nfe)
                shutil.copy(xml_enviado, pasta_repo_nfe)
            else:
                print('XML Autorizado não criado!')

    return cstat, msg_resultado

def gera_cce(nfe, empresa):
    xml_cce = Diretorio.objects.filter(CNPJ=empresa.emit_CNPJ, TipoArquivo='xmlcce').first()

    msg_dados = ''
    msg_ret_ws = ''
    cStat = 0
    msg_resultado = ''
    descEventoAcentuado = 0
    n_cce = nfe.nCCe + 1 if nfe.nCCe else 1
    dh_correcao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    nProtocoloCCe = ''
    dProtocoloCCe = ''
    proxy = ''
    usuario = ''
    senha = ''

    procCCe = obj_nfe_util.EnviaCCe2G(
        empresa.SiglaWebService,
        empresa.IdentificacaoAmbiente,
        empresa.Certificado,
        empresa.VersaoSchema,
        msg_dados,
        msg_ret_ws,
        cStat,
        msg_resultado,
        nfe.chave_acesso,
        nfe.xJust,
        descEventoAcentuado,
        n_cce,
        dh_correcao,
        nProtocoloCCe,
        dProtocoloCCe,
        proxy,
        usuario,
        senha,
        empresa.LicencaDLL
    )

    xml_cce, msg_dados, msg_ret_ws, cStat, msg_resultado, nProtocoloCCe, dProtocoloCCe = procCCe

    if cStat == 135:
        diretorio_cce = Diretorio.objects.filter(CNPJ=empresa.emit_CNPJ, TipoArquivo='xmlcce').first()
        caminho_xml = diretorio_cce.Diretorio + nfe.ide_nNF + '-procCCe.xml'

        if Path(diretorio_cce.Diretorio).is_dir():
            with open(caminho_xml, 'w', encoding='utf-8') as arquivo:
                arquivo.write(xml_cce)
                arquivo.close()

            root = ET.fromstring(xml_cce)
            ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
            ret_evento = root.find('nfe:retEvento', ns)
            inf_evento = ret_evento.find('nfe:infEvento', ns)

            if inf_evento is not None:
                nfe.cStat = inf_evento.findtext('nfe:cStat', namespaces=ns)
                nfe.status_sefaz = 'Carta de Correção registrada'
                nfe.xMotivo = 'Carta de Correção registrada'
                nfe.nProtEvento = inf_evento.findtext('nfe:nProt', namespaces=ns)
                nfe.dhRegEvento = inf_evento.findtext('nfe:dhRegEvento', namespaces=ns)
                nfe.tpEvento = inf_evento.findtext('nfe:tpEvento', namespaces=ns)
                nfe.nSeqEvento = inf_evento.findtext('nfe:nSeqEvento', namespaces=ns)
                nfe.nCCe = inf_evento.findtext('nfe:nSeqEvento', namespaces=ns)
                nfe.save()
                nfe.refresh_from_db()

            # cursor = connection.cursor()
            # cursor.execute("EXEC acertaNFE_CCE %s, %s", [diretorio_cce.Diretorio, nfe.ide_nNF + '-procCCe.xml'])

            shutil.copy(caminho_xml, get_path_repo(nfe, empresa))

    return cStat, msg_resultado

def cancela_nfe(nfe, empresa):
    xml_cancelado = ''
    msg_dados = ''
    msg_ret_ws = ''
    status = 0
    msg_resultado = ''
    protocolo_canc = ''
    data_protocolo_canc = ''
    dh_evento = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    procCancNFe = obj_nfe_util.CancelaNFEvento(
        empresa.SiglaWebService,
        empresa.IdentificacaoAmbiente,
        empresa.Certificado,
        empresa.VersaoSchema,
        msg_dados,
        msg_ret_ws,
        status,
        msg_resultado,
        nfe.chave_acesso,
        nfe.nProt,
        nfe.xJust,
        dh_evento,
        protocolo_canc,
        data_protocolo_canc,
        '',
        '',
        '',
        empresa.LicencaDLL
    )

    xml_cancelado, msg_dados, msg_ret_ws, status, msg_resultado, protocolo_canc, data_protocolo_canc = procCancNFe

    if status == 135:
        if nfe.ide_mod == 55:
            tipo_arquivo_cancelado = 'xmlCancelado'
            diretorio_repo_cancelado = Diretorio.objects.filter(CNPJ=empresa.emit_CNPJ, TipoArquivo='contabilidadeCanc').first()
        elif nfe.ide_mod == 65:
            tipo_arquivo_cancelado = 'xmlCanceladoNFCe'

        diretorio_cancelado = Diretorio.objects.filter(CNPJ=empresa.emit_CNPJ, TipoArquivo=tipo_arquivo_cancelado).first()
        caminho_xml = diretorio_cancelado.Diretorio + nfe.ide_nNF + '-procCancNFe.xml'

        if Path(diretorio_cancelado.Diretorio).is_dir():
            with open(caminho_xml, 'w', encoding='utf-8') as arquivo:
                arquivo.write(xml_cancelado)
                arquivo.close()

            root = ET.fromstring(xml_cancelado)
            ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
            ret_evento = root.find('nfe:retEvento', ns)
            inf_evento = ret_evento.find('nfe:infEvento', ns)

            if inf_evento is not None:
                nfe.cStat = inf_evento.findtext('nfe:cStat', namespaces=ns)
                nfe.status_sefaz = 'Cancelamento registrado'
                nfe.xMotivo = 'Cancelamento registrado'
                nfe.nProtEvento = inf_evento.findtext('nfe:nProt', namespaces=ns)
                nfe.dhRegEvento = inf_evento.findtext('nfe:dhRegEvento', namespaces=ns)
                nfe.tpEvento = inf_evento.findtext('nfe:tpEvento', namespaces=ns)
                nfe.nSeqEvento = inf_evento.findtext('nfe:nSeqEvento', namespaces=ns)
                nfe.save()
                nfe.refresh_from_db()

            if int(nfe.Pedido) > 0:
                cnpj_formatado = f'{empresa.emit_CNPJ[:2]}.{empresa.emit_CNPJ[2:5]}.{empresa.emit_CNPJ[5:8]}/{empresa.emit_CNPJ[8:12]}-{empresa.emit_CNPJ[12:]}'

                corpo_email = f'Nota Fiscal {nfe.ide_nNF} cancelada na SEFAZ, referente ao pedido {nfe.Pedido}.\n'
                corpo_email += f'Empresa: {empresa.emit_xNome}, CNPJ {cnpj_formatado}.\n'
                corpo_email += f'Motivo do cancelamento: {nfe.xJust}'

                email_para = 'tarciana.oliveira@lanmax.com.br'
                cc = 'amanda@lanmax.com.br,renan@lanmax.com.br'
                titulo = f'Cancelamento da Nota Fiscal {nfe.ide_nNF}'

                # cursor.execute("EXEC acertaNFE_Cancelamento %s, %s", [diretorio_cancelado.Diretorio, nfe.ide_nNF + '-procCancNFe.xml'])

            if nfe.ide_mod == 55:
                shutil.copy(caminho_xml, diretorio_repo_cancelado.Diretorio)

            shutil.copy(caminho_xml, get_path_repo(nfe, empresa))
            cursor = connection.cursor()

            cursor.execute("SELECT TOP 1 usuario FROM NFe_Auditoria_400 WHERE pedido = %s AND NF = %s AND Status Like %s AND usuario <> %s AND usuario NOT LIKE %s ORDER BY data_historico DESC", [nfe.Pedido, nfe.ide_nNF, 'Aut%', 'sa', 'NT SERVICE%'])
            result = cursor.fetchone()
        
            if int(nfe.Pedido) < 100000000 and int(nfe.Pedido) > 0:
                db = 'greenmotor'
                cursor.execute("EXEC AS LOGIN=%s;EXEC GreenMotor.dbo.Pedido_09Cancela %s, %s", [result[0], nfe.Pedido, 1])
            elif int(nfe.Pedido) >= 100000000:
                db = 'lanmax'
                cursor.execute("EXEC AS LOGIN=%s;EXEC Lanmax.dbo.Pedido_09Cancela %s, %s", [result[0], nfe.Pedido, 1])
            
            cursor.execute('REVERT;')

            if int(nfe.Pedido) > 0:
                novo_email = EmailsAEnviar.objects.using(db).get_or_create(
                    email_to = email_para,
                    email_cc = cc,
                    assunto = titulo,
                    email_body = corpo_email,
                    body_format = 'plain',
                    attachments = None,
                    data = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    status = 0
                )

    return status, msg_resultado

def gera_xmlgnre(nfe, empresa, detalhamento_receita, data_vencimento, data_pagamento):
    if tem_gnre(nfe.id_nfe, empresa.ide_serie):
        receita = '100099'
        valor = nfe.TotalICMS_vST if nfe.TotalICMS_vST else 0
        prefixo_arquivo = 'gnre_'
    elif gera_difal(nfe.id_nfe, empresa.ide_serie):
        receita = '100102'
        valor = nfe.TotalICMS_vICMSUFDest_Opc if nfe.TotalICMS_vICMSUFDest_Opc else 0
        prefixo_arquivo = 'difal_'
    elif gera_fcp(nfe.id_nfe, empresa.ide_serie):
        receita = '100129'
        valor = nfe.TotalICMS_vFCPUFDest_Opc if nfe.TotalICMS_vFCPUFDest_Opc else 0
        prefixo_arquivo = 'fcp_'
    else:
        receita = ''
        prefixo_arquivo = ''

    endereco_emitente = empresa.emit_xLgr + ', ' + (empresa.emit_nro if empresa.emit_nro else 'S/N')

    xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?><TLote_GNRE versao="2.00" xmlns="http://www.gnre.pe.gov.br"><guias>'
    xml = xml + f'<TDadosGNRE versao="2.00"><ufFavorecida>{nfe.dest_UF}</ufFavorecida><tipoGnre>0</tipoGnre>'
    xml = xml + f'<contribuinteEmitente><identificacao><CNPJ>{empresa.emit_CNPJ}</CNPJ></identificacao><razaoSocial>{empresa.emit_xNome}</razaoSocial>'
    xml = xml + f'<endereco>{endereco_emitente}</endereco><municipio>{str(empresa.emit_cMun)[-5:]}</municipio><uf>{empresa.emit_UF}</uf>'
    xml = xml + f'<cep>{empresa.emit_CEP}</cep><telefone>{empresa.emit_fone}</telefone></contribuinteEmitente><itensGNRE><item><receita>{receita}</receita>'

    if detalhamento_receita:
        xml = xml + f'<detalhamentoReceita>{detalhamento_receita}</detalhamentoReceita>'

    documento_origem = GNRE_DocumentosOrigem.objects.filter(UF=nfe.dest_UF, Receita=receita).first()

    if documento_origem:
        if documento_origem.Codigo == 10:
            doc = nfe.ide_nNF
        elif documento_origem.Codigo in(22, 24):
            doc = nfe.chave_acesso
        else:
            doc = ''

        xml = xml + f'<documentoOrigem tipo="{documento_origem.Codigo}">{doc}</documentoOrigem>'

    produto = GNRE_Produtos.objects.filter(UF=nfe.dest_UF, Receita=receita)

    if produto:
        xml = xml + f'<produto>15</produto>'

    periodo = GNRE_CamposVisiveis.objects.filter(UF=nfe.dest_UF, Receita=receita).first()

    if periodo:
        if periodo.TemPeriodoRef:
            xml = xml + '<referencia>'

            if periodo.TemPeriodo:
                xml = xml + f'<periodo>0</periodo>'

            xml = xml + f'<mes>{nfe.dhRecbto[5:7]}</mes><ano>{nfe.dhRecbto[:4]}</ano></referencia>'

    xml = xml + f'<dataVencimento>{data_vencimento}</dataVencimento>'
    xml = xml + f'<valor tipo="11">{valor:.2f}</valor>'

    valor_gnre = valor

    if receita == '100102':
        gnre_receitas = GNRE_Receitas.objects.filter(UF=nfe.dest_UF, Codigo=100129).first()
        valor_fcp = nfe.TotalICMS_vFCPUFDest_Opc if nfe.TotalICMS_vFCPUFDest_Opc else 0

        if not gnre_receitas and valor_fcp > 0:
            xml = xml + f'<valor tipo="12">{valor_fcp:.2f}</valor>'

            valor_gnre += valor_fcp

    if periodo:
        if periodo.TemInfoDest:
            xml = xml + '<contribuinteDestinatario><identificacao>'
            
            if nfe.dest_indIEDest == '1':
                xml = xml + f'<IE>{nfe.dest_IE.strip()}</IE></identificacao>'
            else:
                if nfe.sTP == 1:
                    xml = xml + f'<CPF>{nfe.dest_CPF}</CPF></identificacao>'
                else:
                    xml = xml + f'<CNPJ>{nfe.dest_CNPJ}</CNPJ></identificacao>'

                xml = xml + f'<razaoSocial>{nfe.dest_xNome.replace('&','&amp;')}</razaoSocial><municipio>{nfe.dest_cMun[-5:]}</municipio>'

            xml = xml + '</contribuinteDestinatario>'
    
    campos_adicionais = GNRE_CamposAdicionais.objects.filter(UF=nfe.dest_UF, Receita=receita, Obrigatorio=True).first()

    if campos_adicionais:
        if campos_adicionais.Codigo == 117:
            valor_campos_adicionais = datetime.now().strftime('%Y-%m-%d')
        else:
            valor_campos_adicionais = nfe.chave_acesso

        xml = xml + f'<camposExtras><campoExtra><codigo>{campos_adicionais.Codigo}</codigo><valor>{valor_campos_adicionais}</valor></campoExtra></camposExtras>'

    xml = xml + f'</item></itensGNRE><valorGNRE>{valor_gnre:.2f}</valorGNRE>'
    xml = xml + f'<dataPagamento>{data_pagamento}</dataPagamento></TDadosGNRE></guias></TLote_GNRE>'

    xml_gnre = Diretorio.objects.filter(CNPJ=empresa.emit_CNPJ, TipoArquivo='gnre').first()
    caminho_gnre = xml_gnre.Diretorio + nfe.ide_nNF
    arquivo_gnre = caminho_gnre + '\\' + prefixo_arquivo + nfe.ide_nNF + '.xml'

    if not Path(caminho_gnre).is_dir():
        Path(caminho_gnre).mkdir(parents=True, exist_ok=True)

    if Path(caminho_gnre).is_dir():
        with open(arquivo_gnre, 'w', encoding='utf-8') as arquivo:
            arquivo.write(xml)
            arquivo.close()

def envia_gnre(nfe, empresa, receita):
    if receita == 100099:
        prefixo_arquivo = 'gnre_'
    elif receita == 100102:
        prefixo_arquivo = 'difal_'
    elif receita == 100129:
        prefixo_arquivo = 'fcp_'
    else:
        prefixo_arquivo = ''

    status = 0

    xml_gnre = Diretorio.objects.filter(CNPJ=empresa.emit_CNPJ, TipoArquivo='gnre').first()
    caminho_gnre = xml_gnre.Diretorio + nfe.ide_nNF
    arquivo_gnre = caminho_gnre + '\\' + prefixo_arquivo + nfe.ide_nNF + '.xml'

    if Path(caminho_gnre).is_dir():
        if Path(arquivo_gnre).is_file():
            with open(arquivo_gnre, "r", encoding="utf-8") as f:
                xml = f.read()

            posicao_tlote = xml.find('<TLote_GNRE')
            xml_gnre = xml[posicao_tlote:]
            msg_retws = ''
            msg_resultado = ''
            nro_recibo = ''
            dh_recibo = ''
            t_est_proc = ''
            proxy = ''
            usuario = ''
            senha = ''

            resultado = obj_nfe_util.EnviaGNRE(empresa.IdentificacaoAmbiente, empresa.Certificado, '2.00', xml_gnre, msg_retws, msg_resultado, nro_recibo, dh_recibo, t_est_proc, proxy, usuario, senha)

            status, xml_gnre, msg_retws, msg_resultado, nro_recibo, dh_recibo, t_est_proc = resultado
            
            if status == 100:
                if int(nfe.Pedido) < 100000000:
                    pedido = Pedido.objects.using('greenmotor').get(cod_pedido=nfe.Pedido)
                else:
                    pedido = Pedido.objects.using('lanmax').get(cod_pedido=nfe.Pedido)

                if receita == 100099:
                    if pedido.gnre_protocolo != nro_recibo:
                        pedido.gnre_protocolo = nro_recibo
                elif receita == 100102:
                    if pedido.difal_protocolo != nro_recibo:
                        pedido.difal_protocolo = nro_recibo
                elif receita == 100129:
                    if pedido.fcp_protocolo != nro_recibo:
                        pedido.fcp_protocolo = nro_recibo

                pedido.save()
                pedido.refresh_from_db()

    return status

def busca_gnre(nfe, empresa, nro_recibo, receita):
    msg_dados = ''
    msg_retws = ''
    msg_resultado = ''
    base64_pdf = ''
    status = 0
    proxy = ''
    usuario = ''
    senha = ''

    resultado = obj_nfe_util.BuscaGNRE(empresa.IdentificacaoAmbiente, empresa.Certificado, '2.00PDF', msg_dados, msg_retws, nro_recibo, status, msg_resultado, proxy, usuario, senha)
    msg_dados, msg_retws, base64_pdf, status, msg_resultado = resultado

    if status == 402:
        if receita == 100099:
            prefixo_arquivo = 'gnre_'
        elif receita == 100102:
            prefixo_arquivo = 'difal_'
        elif receita == 100129:
            prefixo_arquivo = 'fcp_'
        else:
            prefixo_arquivo = ''

        xml_gnre = Diretorio.objects.filter(CNPJ=empresa.emit_CNPJ, TipoArquivo='gnre').first()
        caminho_gnre = xml_gnre.Diretorio + nfe.ide_nNF
        arquivo_gnre = caminho_gnre + '\\' + prefixo_arquivo + nfe.ide_nNF + '_protocolo_' + nro_recibo + '.xml'
        nome_pdf = caminho_gnre + '\\' + prefixo_arquivo + nfe.ide_nNF + '.pdf'

        if Path(caminho_gnre).is_dir():
            with open(arquivo_gnre, 'w', encoding='utf-8') as arquivo:
                arquivo.write(base64_pdf)
                arquivo.close()

        inserir_dados_gnre(nfe, arquivo_gnre, base64_pdf)
        converter_base64_pdf(caminho_gnre, nome_pdf, base64_pdf)

    return status

def inserir_dados_gnre(nfe, arquivo, base64_pdf):
    root = ET.fromstring(base64_pdf)
    ns = {'gnre': 'http://www.gnre.pe.gov.br'}
    nro_recibo_tag = root.find('.//gnre:numeroRecibo', ns)
    uf_favorecida_tag = root.find('.//gnre:ufFavorecida', ns)
    receita_tag = root.find('.//gnre:itensGNRE/gnre:item/gnre:receita', ns)
    emit_cgc_tag = root.find('.//gnre:contribuinteEmitente/gnre:identificacao/gnre:CNPJ', ns)
    emit_razao_social_tag = root.find('.//gnre:contribuinteEmitente/gnre:razaoSocial', ns)
    emit_endereco_tag = root.find('.//gnre:contribuinteEmitente/gnre:endereco', ns)
    emit_uf_tag = root.find('.//gnre:contribuinteEmitente/gnre:uf', ns)
    cod_emit_mun_tag = root.find('.//gnre:contribuinteEmitente/gnre:municipio', ns)
    cep_tag = root.find('.//gnre:contribuinteEmitente/gnre:cep', ns)
    telefone_tag = root.find('.//gnre:contribuinteEmitente/gnre:telefone', ns)
    ie_tag = root.find('.//gnre:itensGNRE/gnre:item/gnre:contribuinteDestinatario/gnre:identificacao/gnre:IE', ns)
    cpf_tag = root.find('.//gnre:itensGNRE/gnre:item/gnre:contribuinteDestinatario/gnre:identificacao/gnre:CPF', ns)
    cnpj_tag = root.find('.//gnre:itensGNRE/gnre:item/gnre:contribuinteDestinatario/gnre:identificacao/gnre:CNPJ', ns)
    cod_dest_mun_tag = root.find('.//gnre:itensGNRE/gnre:item/gnre:contribuinteDestinatario/gnre:municipio', ns)
    produto_tag = root.find('.//gnre:itensGNRE/gnre:item/gnre:produto', ns)
    vencimento_tag = root.find('.//gnre:itensGNRE/gnre:item/gnre:dataVencimento', ns)
    pagamento_tag = root.find('.//gnre:dataLimitePagamento', ns)
    mes_ref_tag = root.find('.//gnre:itensGNRE/gnre:item/gnre:referencia/gnre:mes', ns)
    ano_ref_tag = root.find('.//gnre:itensGNRE/gnre:item/gnre:referencia/gnre:ano', ns)
    infos_tag = root.findall('.//gnre:informacoesComplementares/gnre:informacao', ns)
    valores_tag = root.findall('.//gnre:itensGNRE/gnre:item/gnre:valor', ns)
    valor_gnre_tag = root.find('.//gnre:valorGNRE', ns)
    linha_dig_tag = root.find('.//gnre:linhaDigitavel', ns)
    codbar_tag = root.find('.//gnre:codigoBarras', ns)
    num_controle_tag = root.find('.//gnre:nossoNumero', ns)

    nro_recibo = nro_recibo_tag.text if nro_recibo_tag is not None else ''
    uf_favorecida = uf_favorecida_tag.text if uf_favorecida_tag is not None else ''
    receita = receita_tag.text if receita_tag is not None else ''
    emit_cgc = emit_cgc_tag.text if emit_cgc_tag is not None else ''
    emit_razao_social = emit_razao_social_tag.text if emit_razao_social_tag is not None else ''
    emit_endereco = emit_endereco_tag.text if emit_endereco_tag is not None else ''
    emit_uf = emit_uf_tag.text if emit_uf_tag is not None else ''
    cod_emit_mun = cod_emit_mun_tag.text if cod_emit_mun_tag is not None else ''
    
    tab_uf = TabUF.objects.filter(UF=emit_uf).first()
    cod_emit_uf = tab_uf.ID if tab_uf is not None else ''
        
    codigo = str(cod_emit_uf) + str(cod_emit_mun)
    tab_mun = TabMunicipios.objects.get(ID=codigo)
    emit_mun = tab_mun.NOME if tab_mun is not None else ''

    cep = cep_tag.text if cep_tag is not None else ''
    telefone = telefone_tag.text if telefone_tag is not None else ''
    ie = ie_tag.text if ie_tag is not None else ''
    cpf = cpf_tag.text if cpf_tag is not None else '00000000000'
    cnpj = cnpj_tag.text if cnpj_tag is not None else '00000000000000'
    dest_cgc = cpf if cpf != '00000000000' else cnpj
    cod_dest_mun = cod_dest_mun_tag.text if cod_dest_mun_tag is not None else ''

    tab_uf = TabUF.objects.filter(UF=uf_favorecida).first()
    cod_dest_uf = tab_uf.ID

    if cod_dest_mun != '':
        codigo = str(cod_dest_uf) + str(cod_dest_mun)
        tab_mun = TabMunicipios.objects.get(ID=codigo)
        dest_mun = tab_mun.NOME if tab_mun is not None else ''
    else:
        dest_mun = ''

    prod = produto_tag.text if produto_tag is not None else ''

    if prod != '':
        gnre_produto = GNRE_Produtos.objects.filter(UF=uf_favorecida, Receita=receita, Codigo=prod).first()
        produto = gnre_produto.Descricao if gnre_produto is not None else ''
    else:
        produto = ''

    vencimento = vencimento_tag.text if vencimento_tag is not None else ''
    pagamento = pagamento_tag.text if pagamento_tag is not None else ''
    mes_ref = mes_ref_tag.text if mes_ref_tag is not None else ''
    ano_ref = '/' + ano_ref_tag.text if ano_ref_tag is not None else ''
    mes_ano_ref = mes_ref + ano_ref
    info = ''
    
    for info_tag in infos_tag:
        info += info_tag.text + '\n'

    valor_principal = 0.00
    valor_rj = 0.00
    juros = 0.00
    juros_rj = 0.00
    multa = 0.00
    multa_rj = 0.00

    for valor_tag in valores_tag:
        tipo = valor_tag.get('tipo')
        valor = float(valor_tag.text)

        if tipo == 11:
            valor_principal = valor
        elif tipo == 12:
            valor_rj = valor
        elif tipo == 31:
            multa = valor
        elif tipo == 32:
            multa_rj = valor
        elif tipo == 41:
            juros = valor
        elif tipo == 42:
            juros_rj = valor

    valor_gnre = valor_gnre_tag.text if valor_gnre_tag is not None else 0

    if valor_principal == 0.00:
        valor_principal = valor_gnre

    if valor_rj > 0.00:
        valor_principal += valor_rj

    if juros_rj > 0.00:
        juros += juros_rj

    if multa_rj > 0.00:
        multa += multa_rj

    linha_dig = linha_dig_tag.text if linha_dig_tag is not None else ''
    linha_digitavel = linha_dig[:11] + ' ' + linha_dig[11:12] + ' ' + linha_dig[12:23] + ' ' + linha_dig[23:24] + ' ' + linha_dig[24:35] + ' ' + linha_dig[35:36] + ' ' + linha_dig[36:47] + ' ' + linha_dig[47:48]
    
    codbar = codbar_tag.text if codbar_tag is not None else ''
    num_controle = num_controle_tag.text if num_controle_tag is not None else ''
    gnre_qtdvias = GNRE_QtdVias.objects.filter(UF=uf_favorecida, Receita=receita).first()

    if gnre_qtdvias:
        qtd_vias = gnre_qtdvias.QtdVias
    else:
        qtd_vias = 2

    novo_infboleto, criado = GNRE_InfBoleto.objects.get_or_create(
        Protocolo = nro_recibo,
        UF_Favorecida = uf_favorecida,
        Receita = receita,
        emit_CGC = emit_cgc,
        emit_RazaoSocial = emit_razao_social,
        emit_Endereco = emit_endereco,
        emit_Municipio = emit_mun,
        emit_UF = emit_uf,
        emit_CEP = cep,
        emit_Tel = telefone,
        dest_CGC = dest_cgc,
        dest_Municipio = dest_mun,
        Produto = produto,
        Data_Vencto = vencimento,
        Data_Pagto = pagamento,
        NFe = nfe.ide_nNF,
        MesAnoRef = mes_ano_ref,
        InfCompl = info,
        Valor = valor_principal,
        Att_Mon = 0,
        Juros = juros,
        Multa = multa,
        ValorGNRE = valor_gnre,
        LinhaDigitavel = linha_digitavel,
        CodBar = codbar,
        NumControle = num_controle,
        qtdVias = qtd_vias
    )

    if receita == '100099':
        tipo = 'ST'
    elif receita == '100102':
        tipo = 'DIFAL'
    elif receita == '100129':
        tipo = 'FCP'
    else:
        tipo = ''

    cursor = connection.cursor()
    
    cursor.execute("SELECT TOP 1 usuario FROM NFe_Auditoria_400 WHERE pedido = %s AND NF = %s AND Status Like %s AND usuario <> %s AND usuario NOT LIKE %s ORDER BY data_historico DESC", [nfe.Pedido, nfe.ide_nNF, 'Aut%', 'sa', 'NT SERVICE%'])
    result = cursor.fetchone()

    if int(nfe.Pedido) < 100000000 and int(nfe.Pedido) > 0:
        cursor.execute("EXEC as login=%s;EXEC GreenMotor.dbo.GNRE_Gera %s,%s,%s,%s", [result[0], nfe.Pedido, tipo, nro_recibo, num_controle,])
    else:
        cursor.execute("EXEC as login=%s;EXEC Lanmax.dbo.GNRE_Gera %s,%s,%s,%s", [result[0], nfe.Pedido, tipo, nro_recibo, num_controle,])

    cursor.execute('REVERT;')

def converter_base64_pdf(caminho, nome_arquivo, base64_pdf):
    root = ET.fromstring(base64_pdf)
    ns = {'gnre': 'http://www.gnre.pe.gov.br'}
    pdf_guia = root.find('.//gnre:pdfGuias', ns)

    if pdf_guia is not None:
        conteudo = pdf_guia.text.strip()

        try:
            pdf_bytes = base64.b64decode(conteudo)

            if Path(caminho).is_dir():
                with open(nome_arquivo, 'wb') as arquivo:
                    arquivo.write(pdf_bytes)
                    arquivo.close()
        except Exception as e:
            print(f'Erro na decodificação: {e}')
    else:
        print('Chave pdfGuias não encontrado!')