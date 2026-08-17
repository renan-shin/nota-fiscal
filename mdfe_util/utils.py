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