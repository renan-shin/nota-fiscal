from nfe_util.models import *
from lanmax.models import *
from django.apps import apps
from django.db import connection
from django.conf import settings
from .models import *
from pathlib import Path
from datetime import datetime
import win32com.client
import xml.etree.ElementTree as ET

try:
    obj_mdfe_util = win32com.client.Dispatch("{02E8B11B-30A6-479B-82BF-9AD7ECEE187D}")
    print("Objeto MDF-e carregado com sucesso!")
except Exception as e:
    # import traceback
    # traceback.print_exc()
    print(e)

def consulta_status_mdfe_2g(empresa):
    msg_dados = ''
    msg_ret_ws = ''
    msg_resultado = ''
    tmed = ''
    dh_retorno = ''
    obs = ''
    proxy = ''
    usuario = ''
    senha = ''

    return obj_mdfe_util.ConsultaWS(
        empresa.SiglaWebService_MDFe,
        empresa.emit_UF,
        empresa.IdentificacaoAmbiente,
        empresa.Certificado,
        empresa.Versao_MDFe,
        msg_dados,
        msg_ret_ws,
        msg_resultado,
        tmed,
        dh_retorno,
        obs,
        proxy,
        usuario,
        senha
    )

def consulta_mdfe(empresa, chave_acesso):
    msg_dados = ''
    msg_ret_ws = ''
    msg_resultado = ''
    status = 0
    proxy = ''
    usuario = ''
    senha = ''

    mdfe = obj_mdfe_util.ConsultaMDFe(
        empresa.SiglaWebService_MDFe,
        empresa.IdentificacaoAmbiente,
        empresa.Certificado,
        empresa.Versao_MDFe,
        msg_dados,
        msg_ret_ws,
        msg_resultado,
        chave_acesso,
        proxy,
        usuario,
        senha
    )

    status, msg_dados, msg_ret_ws, msg_resultado = mdfe

    return status, msg_ret_ws, msg_resultado

def encerrar_mdfe(empresa, mdfe):
    msg_dados = ''
    msg_ret_ws = ''
    msg_resultado = ''
    protocolo_enc = ''
    data_protocolo_enc = ''
    status = 0
    proxy = ''
    usuario = ''
    senha = ''
    data_enc = datetime.now().strftime('%Y-%m-%d')
    data_evento = datetime.now().strftime('%Y-%m-%dT%H:%M:%S-03:00')

    try:
        nfe_mdfe = MDFe_ChaveNFe.objects.filter(id_mdfe=mdfe.id_mdfe, ide_serie=empresa.ide_serie).first()
    except MDFe_ChaveNFe.DoesNotExist:
        return None
    
    uf_enc = str(nfe_mdfe.cMunDescarrega)[:2]

    xml_mdfe = obj_mdfe_util.encerraMDFe(
        empresa.SiglaWebService_MDFe,
        empresa.IdentificacaoAmbiente,
        empresa.Certificado,
        empresa.Versao_MDFe,
        msg_dados,
        msg_ret_ws,
        status,
        msg_resultado,
        mdfe.chave_acesso,
        mdfe.nProt,
        data_enc,
        uf_enc,
        nfe_mdfe.cMunDescarrega,
        data_evento,
        protocolo_enc,
        data_protocolo_enc,
        proxy,
        usuario,
        senha,
        empresa.Licenca_MDFe,
    )

    print(xml_mdfe)

    root = ET.fromstring(xml_mdfe)
    namespace = {'ns': 'http://www.portalfiscal.inf.br/mdfe'}
    cstat = root.find('.//ns:retEventoMDFe/ns:infEvento/ns:cStat', namespace)

    if cstat is not None and cstat.text == '135':
        pasta_xml_encerrado = MDFe_Diretorios.objects.filter(cnpj=empresa.emit_CNPJ, tipo_arquivo='xmlEncerrado').first()
        xml_encerrado = pasta_xml_encerrado.diretorio + 'encMDFe_' + mdfe.ide_nMDF + '.xml'

        if Path(pasta_xml_encerrado.diretorio).is_dir():
            with open(xml_encerrado, 'w', encoding='utf-8') as arquivo:
                arquivo.write(xml_mdfe)
                arquivo.close()

            evento = root.find('.//ns:retEventoMDFe/ns:infEvento/ns:xEvento', namespace)
            data_evento = root.find('.//ns:retEventoMDFe/ns:infEvento/ns:dhRegEvento', namespace)
            protocolo = root.find('.//ns:retEventoMDFe/ns:infEvento/ns:nProt', namespace)
            seq_evento = root.find('.//ns:retEventoMDFe/ns:infEvento/ns:nSeqEvento', namespace)
            tipo_evento = root.find('.//ns:retEventoMDFe/ns:infEvento/ns:tpEvento', namespace)

            mdfe.status = evento.text
            mdfe.dProtocoloEnc = data_evento.text
            mdfe.nProtocoloEnc = protocolo.text
            mdfe.nSeqEvento = seq_evento.text
            mdfe.tpEvento = tipo_evento.text
            mdfe.cStat = int(cstat.text)
            mdfe.save()
            mdfe.refresh_from_db()

        return int(cstat.text)
    else:
        return 0

def cancelar_mdfe(empresa, mdfe):
    msg_dados = ''
    msg_ret_ws = ''
    msg_resultado = ''
    protocolo_canc = ''
    data_protocolo_canc = ''
    status = 0
    proxy = ''
    usuario = ''
    senha = ''
    data_evento = datetime.now().strftime('%Y-%m-%dT%H:%M:%S-03:00')

    xml_mdfe = obj_mdfe_util.cancelaMDFe(
        empresa.SiglaWebService_MDFe,
        empresa.IdentificacaoAmbiente,
        empresa.Certificado,
        empresa.Versao_MDFe,
        msg_dados,
        msg_ret_ws,
        status,
        msg_resultado,
        mdfe.chave_acesso,
        mdfe.nProt,
        mdfe.xJust,
        data_evento,
        protocolo_canc,
        data_protocolo_canc,
        proxy,
        usuario,
        senha,
        empresa.Licenca_MDFe,
    )

    print(xml_mdfe)

    return None

def consolida_mdfe(empresa, mdfe):
    status, msg_resultado, chave_mdfe = gera_chave_mdfe(empresa, mdfe)

    # if status == 5601:
    #     mdfe.chave_acesso = chave_mdfe
    #     mdfe.save()
    #     mdfe.refresh_from_db()

    ide = ide_mdfe(empresa, mdfe)
    emit = emit_mdfe(empresa)
    rodo = rodo_mdfe(empresa, mdfe)
    inf_doc = inf_mun_descarga(empresa, mdfe)
    seg_opc = ''
    tot = tot_mdfe(mdfe)
    lacres_opc = ''
    inf_adic_opc = inf_adic_mdfe(mdfe)
    aut_xml_opc = ''
    inf_resptec_opc = ''
    inf_mdfe_supl_opc, status_qrcode, msg_resultado = qrcode_mdfe(empresa, mdfe)

    # if status_qrcode == 6200:
    #     mdfe.qrCode = inf_mdfe_supl_opc
    #     mdfe.save()
    #     mdfe.refresh_from_db()

    prop_pred_opc = ''

    xml = obj_mdfe_util.MDFe_NT2020001(
        empresa.Versao_MDFe,
        chave_mdfe,
        ide,
        emit,
        rodo,
        inf_doc,
        seg_opc,
        tot,
        lacres_opc,
        aut_xml_opc,
        inf_adic_opc,
        inf_resptec_opc,
        inf_mdfe_supl_opc,
        prop_pred_opc
    )

    pasta_xml_enviado = MDFe_Diretorios.objects.filter(cnpj=empresa.emit_CNPJ, tipo_arquivo='xmlEnviado').first()
    xml_enviado = pasta_xml_enviado.diretorio + 'MDFe_' + mdfe.ide_nMDF + '.xml'

    if Path(pasta_xml_enviado.diretorio).is_dir():
        with open(xml_enviado, 'w', encoding='utf-8') as arquivo:
            arquivo.write(xml)
            arquivo.close()

def envia_mdfe(empresa, mdfe):
    pasta_xml_enviado = MDFe_Diretorios.objects.filter(cnpj=empresa.emit_CNPJ, tipo_arquivo='xmlEnviado').first()
    xml_enviado = pasta_xml_enviado.diretorio + 'MDFe_' + mdfe.ide_nMDF + '.xml'

    if Path(pasta_xml_enviado.diretorio).is_dir():
        with open(xml_enviado, "r", encoding="utf-8") as f:
            xml = f.read()

        msg_dados = '',
        msg_ret_ws = '',
        msg_resultado = '',
        status = 0,
        protocolo = '',
        nro_protocolo = ''
        dh_protocolo = ''
        proxy = ''
        usuario = ''
        senha = ''
        xml_assinado = ''

        retorno = obj_mdfe_util.EnviaMDFeSincrono(
            empresa.SiglaWebService,
            empresa.Certificado,
            empresa.Versao_MDFe,
            msg_dados,
            msg_ret_ws,
            status,
            msg_resultado,
            protocolo,
            nro_protocolo,
            dh_protocolo,
            xml_assinado,
            proxy,
            usuario,
            senha,
            empresa.Licenca_MDFe
        )

        print(retorno)

def gera_chave_mdfe(empresa, mdfe):
    ano = datetime.now().strftime('%y')
    mes = datetime.now().strftime('%m')
    status = 0
    msg_resultado = ''
    cdfe = ''
    cdv = ''
    chave_mdfe = ''

    resultado = obj_mdfe_util.CriaChaveDFe(
        empresa.emit_cUF,
        ano,
        mes,
        empresa.emit_CNPJ,
        empresa.ide_mod_MDFe,
        empresa.ide_serie,
        mdfe.ide_nMDF,
        mdfe.ide_tpEmis,
        empresa.ChaveSeguranca,
        msg_resultado,
        cdfe,
        cdv,
        chave_mdfe,
    )

    status, msg_resultado, cdfe, cdv, chave_mdfe = resultado

    return status, msg_resultado, chave_mdfe

def ide_mdfe(empresa, mdfe):
    veiculo = mdfe.id_veiculo

    if veiculo.id_proprietario_id:
        ide_tpTransp_Opc = '2'
    else:
        ide_tpTransp_Opc = ''

    cmdf = mdfe.chave_acesso[35:43]
    cdv = mdfe.chave_acesso[43:44]
    ide_dhEmi = datetime.now().strftime('%Y-%m-%dT%H:%M:%S-03:00')
    inf_mun = inf_mun_carrega(empresa, mdfe)
    inf_perc = inf_perc_mdfe(empresa, mdfe)
    ide_hd_ini_viagem_opc = ''
    ide_ind_canal_verde_opc = '0'
    ide_ind_carrega_posterior_opc = '0'

    return obj_mdfe_util.ide_v3a(
        empresa.emit_cUF,
        empresa.IdentificacaoAmbiente,
        mdfe.ide_tpEmit,
        ide_tpTransp_Opc,
        empresa.ide_mod_MDFe,
        empresa.ide_serie,
        mdfe.ide_nMDF,
        cmdf,
        cdv,
        mdfe.ide_modal,
        ide_dhEmi,
        mdfe.ide_tpEmis,
        mdfe.ide_procEmi,
        mdfe.ide_verProc,
        mdfe.ide_UFIni,
        mdfe.ide_UFFim,
        inf_mun,
        inf_perc,
        ide_hd_ini_viagem_opc,
        ide_ind_canal_verde_opc,
        ide_ind_carrega_posterior_opc
    )

def inf_mun_carrega(empresa, mdfe):
    nfes = MDFe_ChaveNFe.objects.filter(id_mdfe=mdfe.id_mdfe, ide_serie=empresa.ide_serie).values('cMunCarrega', 'xMunCarrega').distinct()
    inf_mun = ''

    for nf in nfes:
        inf_mun = inf_mun + obj_mdfe_util.infMunCarrega(nf['cMunCarrega'], nf['xMunCarrega'])

    return inf_mun

def inf_perc_mdfe(empresa, mdfe):
    percurso = MDFe_Percursos.objects.filter(id_mdfe=mdfe.id_mdfe, ide_serie=empresa.ide_serie).order_by('ordem')
    inf_perc = ''

    for perc in percurso:
        inf_perc = inf_perc + obj_mdfe_util.infPercurso(perc.uf)

    return inf_perc

def emit_mdfe(empresa):
    return obj_mdfe_util.emit(
        empresa.emit_CNPJ,
        empresa.emit_IE,
        empresa.emit_xNome,
        empresa.emit_xFant if empresa.emit_xFant else '',
        empresa.emit_xLgr,
        empresa.emit_nro,
        empresa.emit_xCpl if empresa.emit_xCpl else '',
        empresa.emit_xBairro,
        empresa.emit_cMun,
        empresa.emit_xMun,
        empresa.emit_CEP,
        empresa.emit_cUF,
        empresa.emit_fone,
        empresa.emit_eMail
    )

def rodo_mdfe(empresa, mdfe):
    veiculo = mdfe.id_veiculo
    
    if veiculo.id_proprietario_id:
        infANTT_Grupo_Opc = inf_antt(empresa)
    else:
        infANTT_Grupo_Opc = ''

    veic_tracao_grupo = veic_principal(mdfe)
    veic_reboque_grupo_opc = ''
    cod_ag_porto_opc = ''
    lac_rodo_grupo_opc = ''

    return obj_mdfe_util.rodo_v3(
        empresa.Versao_MDFe,
        infANTT_Grupo_Opc,
        veic_tracao_grupo,
        veic_reboque_grupo_opc,
        cod_ag_porto_opc,
        lac_rodo_grupo_opc
    )

def inf_antt(empresa):
    rntrc = ''
    inf_ciot_grupo_opc = ''
    vale_ped_grupo_opc = ''
    inf_contratante_grupo_opc = inf_cont(empresa)
    inf_pag_grupo_opc = ''

    return obj_mdfe_util.infANTT_NT2021001(
        rntrc,
        inf_ciot_grupo_opc,
        vale_ped_grupo_opc,
        inf_contratante_grupo_opc,
        inf_pag_grupo_opc
    )

def inf_cont(empresa):
    cpf = ''
    idEstrangeiro = ''
    NroContrato = ''
    vContratoGlobal = 0
    
    return obj_mdfe_util.infCont_NT2022001(
        empresa.emit_xNome,
        cpf,
        empresa.emit_CNPJ,
        idEstrangeiro,
        NroContrato,
        vContratoGlobal
    )

def veic_principal(mdfe):
    veiculo = mdfe.id_veiculo
    motorista = condutor(mdfe)
    prop = proprietario(mdfe)

    return obj_mdfe_util.veicPrincipal_v3(
        '',
        veiculo.placa,
        veiculo.renavam,
        veiculo.tara,
        veiculo.capacidade_kg if veiculo.capacidade_kg else '',
        veiculo.capacidade_m3 if veiculo.capacidade_m3 else '',
        prop,
        motorista,
        veiculo.tipo_rodado,
        veiculo.tipo_carroceria,
        veiculo.uf
    )

def condutor(mdfe):
    motorista = mdfe.id_condutor

    return obj_mdfe_util.Condutor(
        motorista.nome,
        motorista.cpf
    )

def proprietario(mdfe):
    veiculo = mdfe.id_veiculo

    if veiculo.id_proprietario_id:
        prop = veiculo.id_proprietario

        return obj_mdfe_util.prop_v10a(
            prop.cpf if prop.cpf else '',
            prop.cnpj if prop.cnpj else '',
            prop.rntrc if prop.rntrc else '',
            prop.razao_social if prop.razao_social else '',
            prop.ie if prop.ie else '',
            prop.uf if prop.uf else '',
            prop.tp_prop if prop.tp_prop else ''
        )
    else:
        return ''

def inf_mun_descarga(empresa, mdfe):
    nfes = MDFe_ChaveNFe.objects.filter(id_mdfe=mdfe.id_mdfe, ide_serie=empresa.ide_serie).values('cMunDescarrega', 'xMunDescarrega').distinct()
    inf_mun = ''

    for nf in nfes:
        inf_cte_grupo_opc = ''
        inf_nfe_grupo_opc = inf_nfe(empresa, mdfe, nf['cMunDescarrega'])
        inf_mdfe_grupo_opc = ''

        inf_mun = inf_mun + obj_mdfe_util.infMunDescarga(nf['cMunDescarrega'], nf['xMunDescarrega'], inf_cte_grupo_opc, inf_nfe_grupo_opc, inf_mdfe_grupo_opc)

    return inf_mun

def inf_nfe(empresa, mdfe, cmun):
    nfes = MDFe_ChaveNFe.objects.filter(id_mdfe=mdfe.id_mdfe, ide_serie=empresa.ide_serie, cMunDescarrega=cmun)
    inf_nfe = ''

    for nf in nfes:
        seg_cod_barra_opc = ''
        ind_reentrega_opc = ''
        inf_unid_transp_grupo_opc = ''
        peri_grupo_opc = ''

        inf_nfe = inf_nfe + obj_mdfe_util.infNFe_v3(nf.chave_nfe, seg_cod_barra_opc, ind_reentrega_opc, inf_unid_transp_grupo_opc, peri_grupo_opc)

    return inf_nfe

def tot_mdfe(mdfe):
    return obj_mdfe_util.tot_v3(
        mdfe.total_qCTe_Opc if mdfe.total_qCTe_Opc else 0,
        mdfe.total_qNFe_Opc if mdfe.total_qNFe_Opc else 0,
        mdfe.total_qMDFe_Opc if mdfe.total_qMDFe_Opc else 0,
        mdfe.total_vCarga if mdfe.total_vCarga else 0,
        mdfe.total_cUnid if mdfe.total_cUnid else 0,
        mdfe.total_qCarga if mdfe.total_qCarga else 0
    )

def inf_adic_mdfe(mdfe):
    return obj_mdfe_util.infAdic(
        mdfe.infAdFisco_Opc if mdfe.infAdFisco_Opc else '',
        mdfe.infCpl_Opc if mdfe.infCpl_Opc else ''
    )

def qrcode_mdfe(empresa, mdfe):
    url = 'https://dfe-portal.svrs.rs.gov.br/mdfe/qrCode'
    qrcode = ''
    resultado = 0
    msg_resultado = ''

    retorno = obj_mdfe_util.infMDFeSupl(
        url,
        mdfe.chave_acesso,
        empresa.IdentificacaoAmbiente,
        empresa.Certificado,
        qrcode,
        resultado,
        msg_resultado
    )

    qrcode, url, resultado, msg_resultado = retorno

    return qrcode, resultado, msg_resultado