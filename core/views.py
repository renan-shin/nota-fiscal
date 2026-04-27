from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import *
from lanmax.models import *
from nfe_util_2g.utils import *
from django.apps import apps
from email_validator import validate_email, EmailNotValidError
import os

@login_required
def index(request):
    empresas = Empresa.objects.all()
    return render(request, 'core/index.html', {'empresas': empresas})

@login_required
def nfe_edit(request, empresa_filial, id_nfe):
    try:
        empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
        nome_tabela = apps.get_model('core', empresa.Tabela)
        nome_tabela_itens = apps.get_model('core', empresa.TabelaItens)
    except Empresa.DoesNotExist:
        messages.error(request, 'Empresa não encontrada!')
        # empresas = Empresa.objects.all()
        # return render(request, 'core/index.html', {'empresas': empresas})
        return redirect('core_index')

    try:
        nfe = nome_tabela.objects.get(id_nfe=id_nfe)
    except nome_tabela.DoesNotExist:
        messages.error(request, 'Nota Fiscal não encontrada!')
        #empresas = Empresa.objects.all()
        #return render(request, 'core/index.html', {'empresas': empresas})
        return redirect('core_index')

    opcoes_envio_email = (
        ('0', 'Enviado'),
        ('1', 'Enviado (GNRE)'),
        ('2', 'A Enviar'),
        ('3', 'Erro'),
    )

    opcoes_contribuinte = (
        ('1', 'Contribuinte ICMS'),
        ('2', 'Contribuinte Isento de Inscrição no Cadastro de Contribuintes do ICMS'),
        ('9', 'Não Contribuinte, que pode ou não possuir Inscrição Estadual no Cadastro de Contribuinte do ICMS')
    )

    opcoes_modfrete = (
        ('0', 'Por Conta do Emitente'),
        ('1', 'Por Conta do Destinatário'),
        ('2', 'Por Conta de Terceiros'),
        ('9', 'Sem Frete')
    )

    estados = TabUF.objects.all().order_by('UF')

    status_nfe = nome_tabela.objects.values_list('status_sefaz', flat=True).distinct().order_by('status_sefaz')

    if request.method == 'GET':
        return render(request, 'core/nfe-edit.html', {'nfe': nfe, 'empresa': empresa, 'opcoes_envio_email': opcoes_envio_email, 'opcoes_contribuinte': opcoes_contribuinte, 'opcoes_modfrete': opcoes_modfrete, 'estados': estados, 'status_nfe': status_nfe})

    if request.method == 'POST':
        opcao_envio_email = request.POST.get('opcao_envio_email', 3)
        email_cliente = request.POST.get('email_cliente', '')
        opcao_contribuinte = request.POST.get('opcao_contribuinte', 0)
        cnpj_dest = request.POST.get('cnpj_dest', '')
        cpf_dest = request.POST.get('cpf_dest', '')
        cnpj_transp = request.POST.get('cnpj_transp', '')
        ie_dest = request.POST.get('ie_dest', '')
        ie_transp = request.POST.get('ie_transp', '')
        end_transp = request.POST.get('logradouro_transp', '')
        status = request.POST.get('status_nfe', '')
        transmitir = request.POST.get('transmitir_check', False)
        cce = request.POST.get('cce_check', False)
        cancelar = request.POST.get('cancelar_check', False)
        xml_transmitido = request.POST.get('xml_transmitido_check', False)
        adfisco = request.POST.get('adfisco', '')
        infcpl = request.POST.get('infcpl', '')

        if int(opcao_contribuinte) == 9:
            nfe.ide_indFinal = 1
        else:
            nfe.ide_indFinal = 0

        if int(opcao_contribuinte) != 1:
            nfe.dest_IE = None
        else:
            nfe.dest_IE = ie_dest
        # else:
        #     if int(nfe.Pedido) < 100000000 and int(nfe.Pedido) > 0:
        #         db = 'greenmotor'
        #     else:
        #         db = 'lanmax'

        #     pedido = Pedido.objects.using(db).select_related('cod_cliente').get(cod_pedido=int(nfe.Pedido))
        #     nfe.dest_IE = pedido.cod_cliente.inscricao_estadual.replace('.', '').replace('-', '')

        if not controleInterno(int(nfe.Pedido)):
            cursor = connection.cursor()

            cursor.execute("EXEC dbo.calculaTribNFe_400 %s, %s", [nfe.id_nfe, empresa.emit_CNPJ])
            cursor.execute("EXEC dbo.calculaDIFAL_400 %s, %s", [nfe.id_nfe, empresa.ide_serie])

        nfe.ECFRef_mod = opcao_envio_email
        nfe.dest_eMail = email_cliente
        nfe.dest_CPF = cpf_dest.replace('.','').replace('-','')
        nfe.dest_CNPJ = cnpj_dest.replace('/','').replace('.','').replace('-','')
        nfe.transp_CNPJ = cnpj_transp.replace('/','').replace('.','').replace('-','')
        nfe.transporta_IE = ie_transp
        nfe.transporta_xEnder = end_transp
        nfe.status_sefaz = status
        nfe.Transmitir = transmitir
        nfe.CCe = cce
        nfe.Cancelar = cancelar
        nfe.XML_Transmitido = xml_transmitido
        nfe.infAdic_infAdFisco = adfisco
        nfe.infAdic_infCpl = infcpl
        nfe.save()
        nfe.refresh_from_db()
        messages.success(request, 'Dados salvos com sucesso!')
        return render(request, 'core/nfe-edit.html', {'nfe': nfe, 'empresa': empresa, 'opcoes_envio_email': opcoes_envio_email, 'opcoes_contribuinte': opcoes_contribuinte, 'opcoes_modfrete': opcoes_modfrete, 'estados': estados, 'status_nfe': status_nfe, 'form': request.POST})

        # if opcao not in('0','2','3'):
        #     messages.error(request, 'Opção inválida!')
        #     return render(request, 'core/nfe-edit.html', {'nfe': nfe, 'empresa': empresa, 'opcoes': opcoes, 'status_nfe': status_nfe, 'form': request.POST})
        
        # if opcao != '0':
        #     try:
        #         lista_emails = email_cliente.split(';')

        #         for e in lista_emails:
        #             info = validate_email(e.strip(), check_deliverability=False)
        #         # email_cliente = info.normalized

        #         nfe.ECFRef_mod = opcao
        #         nfe.dest_eMail = email_cliente
        #         nfe.status_sefaz = status_nfe
        #         nfe.Transmitir = transmitir
        #         nfe.CCe = cce
        #         nfe.Cancelar = cancelar
        #         nfe.save()
        #         nfe.refresh_from_db()
        #         messages.success(request, 'Dados salvos com sucesso!')
        #         return render(request, 'core/nfe-edit.html', {'nfe': nfe, 'empresa': empresa, 'opcoes': opcoes, 'status_nfe': status_nfe, 'form': request.POST})
        #     except EmailNotValidError as e:
        #         messages.error(request, e)
        #         return render(request, 'core/nfe-edit.html', {'nfe': nfe, 'empresa': empresa, 'opcoes': opcoes, 'status_nfe': status_nfe, 'form': request.POST})
        # else:
        #     nfe.ECFRef_mod = opcao
        #     nfe.status_sefaz = status_nfe
        #     nfe.Transmitir = transmitir
        #     nfe.CCe = cce
        #     nfe.Cancelar = cancelar
        #     nfe.save()
        #     nfe.refresh_from_db()
        #     messages.success(request, 'Dados salvos com sucesso!')
        #     return render(request, 'core/nfe-edit.html', {'nfe': nfe, 'empresa': empresa, 'opcoes': opcoes, 'status_nfe': status_nfe, 'form': request.POST})

def monitoramento_nfe(request):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM MonitoramentoNFe ORDER BY Tempo DESC, Empresa")

    rows = cursor.fetchall()
    keys = ('id_nfe', 'pedido', 'ide_nnf', 'status_sefaz', 'data_emissao', 'frg_xml', 'empresa', 'empresa_filial', 'transmitir', 'cce', 'cancelar', 'tempo', 'gnre_nf', 'difal_nf', 'fcp_nf')

    nfes = [dict(zip(keys, row)) for row in rows]
    
    return render(request, 'core/monitoramento-nfe.html', {'nfes': nfes})

def retransmitir(request, empresa_filial, id_nfe):
    try:
        empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
        nome_tabela = apps.get_model('core', empresa.Tabela)
    except Empresa.DoesNotExist:
        return redirect('core_monitoramento_nfe')

    try:
        nfe = nome_tabela.objects.get(id_nfe=id_nfe)
    except nome_tabela.DoesNotExist:
        return redirect('core_monitoramento_nfe')
    
    if 'Aut' in nfe.status_sefaz or 'Carta' in nfe.status_sefaz or 'Canc' in nfe.status_sefaz:
        return redirect('core_monitoramento_nfe')
    
    nfe.Transmitir = True
    nfe.XML_Transmitido = False
    nfe.status_sefaz = 'NFe não enviada'
    nfe.save()
    nfe.refresh_from_db()

    return redirect('core_monitoramento_nfe')