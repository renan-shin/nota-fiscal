from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from lanmax.models import *
from nfe_util_2g.utils import *
from django.apps import apps
from django.db.models import Value, CharField, IntegerField
from email_validator import validate_email, EmailNotValidError
from datetime import datetime

empresas_greenmotor = [-3102, -3101, -3131, -2003, -2002, -2001, -1033, -1003, -1002, -1001, 8001, 8003, 8004, 8005, 8006, 8007]

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

    try:
        nfe_itens = nome_tabela_itens.objects.filter(id_nfe=id_nfe)
    except nome_tabela_itens.DoesNotExist:
        messages.error(request, 'Itens da Nota Fiscal não encontrada!')
        #empresas = Empresa.objects.all()
        #return render(request, 'core/index.html', {'empresas': empresas})
        return redirect('core_index')
    
    cursor = connection.cursor()

    cursor.execute("SELECT fpn.id_nfe, fpn.ide_serie, fpn.pagamento_nForma, IIF(fpn.pagamento_indPag_Opc = 0, 'Pagamento à vista', 'Pagamento à prazo'), fp.Descricao, fpn.pagamento_vPag FROM FormasPagto_NFE fpn INNER JOIN FormasPagto fp ON fpn.pagamento_tPag = fp.Codigo WHERE id_nfe = %s AND ide_serie = %s ORDER BY fpn.pagamento_nForma", [id_nfe, empresa.ide_serie,])
    rows = cursor.fetchall()

    keys = ('id_nfe', 'ide_serie', 'pagamento_nforma', 'indpag', 'descricao', 'valor',)

    formas_pagto = []

    for row in rows:
        formas_pagto.append(dict(zip(keys, row)))

    opcoes_envio_email = (
        ('0', 'Enviado'),
        ('1', 'Enviado (GNRE)'),
        ('2', 'A Enviar'),
        ('3', 'Erro'),
    )

    opcoes_tipo_emissao = {
        ('1', 'Emissão normal'),
        ('2', 'Contingência FS-IA'),
        ('3', 'Contingência SCAN'),
        ('4', 'Contingência DPEC'),
        ('5', 'Contingência FS-DA'),
        ('6', 'Contingência SVC-AN'),
        ('7', 'Contingência SVC-RS'),
        ('9', 'Contingência off-line da NFC-e')
    }

    opcoes_tipo_nf = {
        ('0', 'Entrada'),
        ('1', 'Saída')
    }

    opcoes_finalidade_nf = {
        ('1', 'NF-e Normal'),
        ('2', 'NF-e Complementar'),
        ('3', 'NF-e Ajuste'),
        ('4', 'Devolução')
    }

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

    opcoes_ind_forma_pagto = (
        ('0', 'Pagamento à vista'),
        ('1', 'Pagamento à prazo')
    )

    opcoes_ind_pres = (
        ('0', 'Não se aplica'),
        ('1', 'Operação presencial'),
        ('2', 'Operação não presencial, pela Internet'),
        ('3', 'Operação não presencial, Teleatendimento'),
        ('4', 'NFC-e em operação com entrega a domicílio'),
        ('9', 'Operação não presencial, outros')
    )

    opcoes_consumidor = (
        ('0', 'Não'),
        ('1', 'Consumidor Final')
    )

    opcoes_local_destino = (
        ('1', 'Operação interna'),
        ('2', 'Operação interestadual'),
        ('3', 'Operação com exterior')
    )

    opcoes_referenciar_nfe = (
        ('0', 'NF-e sem referência'),
        ('1', 'NF-e referenciada'),
        ('2', 'NF-e modelo 1/1A'),
        ('3', 'NF-e de produtor referenciada'),
        ('4', 'CT-e referenciada'),
        ('5', 'Cupom Fiscal referenciado')
    )

    opcoes_tipo_pessoa = (
        ('1', 'Física'),
        ('2', 'Jurídica')
    )

    estados = TabUF.objects.all().order_by('UF')

    status_nfe = nome_tabela.objects.values_list('status_sefaz', flat=True).distinct().order_by('status_sefaz')

    if request.method == 'GET':
        return render(request,
                      'core/nfe-edit.html',
                      {
                          'nfe': nfe,
                          'nfe_itens': nfe_itens,
                          'empresa': empresa,
                          'formas_pagto': formas_pagto,
                          'opcoes_envio_email': opcoes_envio_email,
                          'opcoes_tipo_emissao': opcoes_tipo_emissao,
                          'opcoes_tipo_nf': opcoes_tipo_nf,
                          'opcoes_finalidade_nf': opcoes_finalidade_nf,
                          'opcoes_contribuinte': opcoes_contribuinte,
                          'opcoes_modfrete': opcoes_modfrete,
                          'opcoes_ind_forma_pagto': opcoes_ind_forma_pagto,
                          'opcoes_ind_pres': opcoes_ind_pres,
                          'opcoes_consumidor': opcoes_consumidor,
                          'opcoes_local_destino': opcoes_local_destino,
                          'opcoes_referenciar_nfe': opcoes_referenciar_nfe,
                          'opcoes_tipo_pessoa': opcoes_tipo_pessoa,
                          'estados': estados,
                          'status_nfe': status_nfe})

    if request.method == 'POST':
        cliente = request.POST.get('cliente', '')
        opcao_envio_email = request.POST.get('opcao_envio_email', 3)
        email_cliente = request.POST.get('email_cliente', '')
        opcao_contribuinte = request.POST.get('opcao_contribuinte', 0)
        cnpj_dest = request.POST.get('cnpj_dest', '')
        cpf_dest = request.POST.get('cpf_dest', '')
        ie_dest = request.POST.get('ie_dest', '')
        fone_dest = request.POST.get('fone_dest', '')
        cep_dest = request.POST.get('cep_dest', '')
        logradouro_dest = request.POST.get('logradouro_dest', '')
        numero_dest = request.POST.get('numero_dest', '')
        cpl_dest = request.POST.get('cpl_dest', '')
        estado = request.POST.get('estado', '')
        opcao_modfrete = request.POST.get('opcao_modfrete', '')
        cnpj_transp = request.POST.get('cnpj_transp', '')
        ie_transp = request.POST.get('ie_transp', '')
        end_transp = request.POST.get('logradouro_transp', '')
        mun_transp = request.POST.get('municipio_transp', '')
        uf_transp = request.POST.get('uf_transp', '')
        status = request.POST.get('status_nfe', '')
        transmitir = request.POST.get('transmitir_check', False)
        cce = request.POST.get('cce_check', False)
        cancelar = request.POST.get('cancelar_check', False)
        xml_transmitido = request.POST.get('xml_transmitido_check', False)
        adfisco = request.POST.get('adfisco', '')
        infcpl = request.POST.get('infcpl', '')
        # cobr_nfat = request.POST.get('cobr_nfat', '')
        # cobr_vliq = request.POST.get('cobr_vliq', 0).replace('.', '').replace(',', '.')
        # cobr_vorig = request.POST.get('cobr_vorig', 0).replace('.', '').replace(',', '.')
        xjust = request.POST.get('xjust', '')

        if nfe.status_sefaz != 'NFe não enviada' and int(nfe.ide_mod) == 55 and opcao_envio_email not in('0','1','2','3'):
            messages.error(request, 'Opção de envio de e-mail inválida!')
            return render(request, 'core/nfe-edit.html', {
                'nfe': nfe,
                'nfe_itens': nfe_itens,
                'empresa': empresa,
                'formas_pagto': formas_pagto,
                'opcoes_envio_email': opcoes_envio_email,
                'opcoes_tipo_emissao': opcoes_tipo_emissao,
                'opcoes_tipo_nf': opcoes_tipo_nf,
                'opcoes_finalidade_nf': opcoes_finalidade_nf,
                'opcoes_contribuinte': opcoes_contribuinte,
                'opcoes_modfrete': opcoes_modfrete,
                'opcoes_ind_forma_pagto': opcoes_ind_forma_pagto,
                'opcoes_ind_pres': opcoes_ind_pres,
                'opcoes_consumidor': opcoes_consumidor,
                'opcoes_local_destino': opcoes_local_destino,
                'opcoes_referenciar_nfe': opcoes_referenciar_nfe,
                'opcoes_tipo_pessoa': opcoes_tipo_pessoa,
                'estados': estados,
                'status_nfe': status_nfe,
                'form': request.POST
            })
        
        if opcao_contribuinte not in('1','2','9'):
            messages.error(request, 'Tipo de Contribuinte inválido!')
            return render(request, 'core/nfe-edit.html', {
                'nfe': nfe,
                'nfe_itens': nfe_itens,
                'empresa': empresa,
                'formas_pagto': formas_pagto,
                'opcoes_envio_email': opcoes_envio_email,
                'opcoes_tipo_emissao': opcoes_tipo_emissao,
                'opcoes_tipo_nf': opcoes_tipo_nf,
                'opcoes_finalidade_nf': opcoes_finalidade_nf,
                'opcoes_contribuinte': opcoes_contribuinte,
                'opcoes_modfrete': opcoes_modfrete,
                'opcoes_ind_forma_pagto': opcoes_ind_forma_pagto,
                'opcoes_ind_pres': opcoes_ind_pres,
                'opcoes_consumidor': opcoes_consumidor,
                'opcoes_local_destino': opcoes_local_destino,
                'opcoes_referenciar_nfe': opcoes_referenciar_nfe,
                'opcoes_tipo_pessoa': opcoes_tipo_pessoa,
                'estados': estados,
                'status_nfe': status_nfe,
                'form': request.POST
            })
        
        if opcao_modfrete not in('0','1','2','9'):
            messages.error(request, 'Tipo de Frete inválido!')
            return render(request, 'core/nfe-edit.html', {
                'nfe': nfe,
                'nfe_itens': nfe_itens,
                'empresa': empresa,
                'formas_pagto': formas_pagto,
                'opcoes_envio_email': opcoes_envio_email,
                'opcoes_tipo_emissao': opcoes_tipo_emissao,
                'opcoes_tipo_nf': opcoes_tipo_nf,
                'opcoes_finalidade_nf': opcoes_finalidade_nf,
                'opcoes_contribuinte': opcoes_contribuinte,
                'opcoes_modfrete': opcoes_modfrete,
                'opcoes_ind_forma_pagto': opcoes_ind_forma_pagto,
                'opcoes_ind_pres': opcoes_ind_pres,
                'opcoes_consumidor': opcoes_consumidor,
                'opcoes_local_destino': opcoes_local_destino,
                'opcoes_referenciar_nfe': opcoes_referenciar_nfe,
                'opcoes_tipo_pessoa': opcoes_tipo_pessoa,
                'estados': estados,
                'status_nfe': status_nfe,
                'form': request.POST
            })
        
        if int(nfe.ide_mod) == 55 and opcao_envio_email not in('0','1') and 'shopee+' not in nfe.dest_eMail and nfe.dest_eMail != 'NaoInformado' and nfe.dest_eMail != '@':
            try:
                lista_emails = email_cliente.split(';')

                for e in lista_emails:
                    info = validate_email(e.strip(), check_deliverability=False)
                # email_cliente = info.normalized
            except EmailNotValidError as e:
                messages.error(request, e)
                return render(request, 'core/nfe-edit.html', {
                    'nfe': nfe,
                    'nfe_itens': nfe_itens,
                    'empresa': empresa,
                    'formas_pagto': formas_pagto,
                    'opcoes_envio_email': opcoes_envio_email,
                    'opcoes_tipo_emissao': opcoes_tipo_emissao,
                    'opcoes_tipo_nf': opcoes_tipo_nf,
                    'opcoes_finalidade_nf': opcoes_finalidade_nf,
                    'opcoes_contribuinte': opcoes_contribuinte,
                    'opcoes_modfrete': opcoes_modfrete,
                    'opcoes_ind_forma_pagto': opcoes_ind_forma_pagto,
                    'opcoes_ind_pres': opcoes_ind_pres,
                    'opcoes_consumidor': opcoes_consumidor,
                    'opcoes_local_destino': opcoes_local_destino,
                    'opcoes_referenciar_nfe': opcoes_referenciar_nfe,
                    'opcoes_tipo_pessoa': opcoes_tipo_pessoa,
                    'estados': estados,
                    'status_nfe': status_nfe,
                    'form': request.POST
                })

        if int(opcao_contribuinte) == 9:
            nfe.ide_indFinal = 1
        else:
            nfe.ide_indFinal = 0

        if int(opcao_contribuinte) != 1:
            nfe.dest_IE = None
        else:
            nfe.dest_IE = ie_dest

        if not controleInterno(int(nfe.Pedido)):
            cursor = connection.cursor()

            cursor.execute("EXEC dbo.calculaTribNFe_400 %s, %s", [nfe.id_nfe, empresa.emit_CNPJ])
            cursor.execute("EXEC dbo.calculaDIFAL_400 %s, %s", [nfe.id_nfe, empresa.ide_serie])

        cursor.execute("SELECT Lanmax.dbo.PertenceAoGrupo(%s,%s)", ['Diretoria', request.user.username])
        result = cursor.fetchone()
        
        if result[0] != 0:
            nfe.dest_xNome = cliente
            nfe.ECFRef_mod = opcao_envio_email
            nfe.dest_eMail = email_cliente
            nfe.dest_xLgr = logradouro_dest
            nfe.dest_nro = numero_dest
            nfe.dest_xCpl = cpl_dest
            nfe.dest_fone = fone_dest
            nfe.dest_CEP = cep_dest.replace('-','')
            nfe.status_sefaz = status
            nfe.Transmitir = transmitir
            nfe.CCe = cce
            nfe.Cancelar = cancelar
            nfe.XML_Transmitido = xml_transmitido
            nfe.xJust = xjust

            if nfe.status_sefaz == 'NFe não enviada':
                nfe.dest_CPF = cpf_dest.replace('.','').replace('-','')
                nfe.dest_CNPJ = cnpj_dest.replace('/','').replace('.','').replace('-','')
                nfe.dest_UF = estado
                nfe.transp_CNPJ = cnpj_transp.replace('/','').replace('.','').replace('-','')
                nfe.transporta_IE = ie_transp
                nfe.transporta_xEnder = end_transp
                nfe.infAdic_infAdFisco = adfisco
                nfe.infAdic_infCpl = infcpl
                # nfe.cobr_nFat = cobr_nfat
                # nfe.cobr_vLiq = float(cobr_vliq)
                # nfe.cobr_vOrig = float(cobr_vorig)
                nfe.dest_indIEDest = opcao_contribuinte
                nfe.transporta_CNPJ = cnpj_transp
                nfe.transporta_xEnder = end_transp
                nfe.transporta_xMun = mun_transp
                nfe.transporta_UF = uf_transp
        else:
            if nfe.status_sefaz == 'NFe não enviada':
                nfe.dest_eMail = email_cliente
                nfe.dest_nro = numero_dest
                nfe.dest_xCpl = cpl_dest
                nfe.dest_fone = fone_dest
                nfe.transporta_IE = ie_transp
            else:
                messages.error(request, 'Usuário sem permissão para alterar dados!')
                return render(request, 'core/nfe-edit.html', {
                    'nfe': nfe,
                    'nfe_itens': nfe_itens,
                    'empresa': empresa,
                    'formas_pagto': formas_pagto,
                    'opcoes_envio_email': opcoes_envio_email,
                    'opcoes_tipo_emissao': opcoes_tipo_emissao,
                    'opcoes_tipo_nf': opcoes_tipo_nf,
                    'opcoes_finalidade_nf': opcoes_finalidade_nf,
                    'opcoes_contribuinte': opcoes_contribuinte,
                    'opcoes_modfrete': opcoes_modfrete,
                    'opcoes_ind_forma_pagto': opcoes_ind_forma_pagto,
                    'opcoes_ind_pres': opcoes_ind_pres,
                    'opcoes_local_destino': opcoes_local_destino,
                    'opcoes_referenciar_nfe': opcoes_referenciar_nfe,
                    'opcoes_tipo_pessoa': opcoes_tipo_pessoa,
                    'estados': estados,
                    'status_nfe': status_nfe,
                    'form': request.POST
                })
            
        nfe.save()
        nfe.refresh_from_db()
        messages.success(request, 'Dados salvos com sucesso!')
        return render(request, 'core/nfe-edit.html', {
            'nfe': nfe,
            'nfe_itens': nfe_itens,
            'empresa': empresa,
            'formas_pagto': formas_pagto,
            'opcoes_envio_email': opcoes_envio_email,
            'opcoes_tipo_emissao': opcoes_tipo_emissao,
            'opcoes_tipo_nf': opcoes_tipo_nf,
            'opcoes_finalidade_nf': opcoes_finalidade_nf,
            'opcoes_contribuinte': opcoes_contribuinte,
            'opcoes_modfrete': opcoes_modfrete,
            'opcoes_ind_forma_pagto': opcoes_ind_forma_pagto,
            'opcoes_ind_pres': opcoes_ind_pres,
            'opcoes_consumidor': opcoes_consumidor,
            'opcoes_local_destino': opcoes_local_destino,
            'opcoes_referenciar_nfe': opcoes_referenciar_nfe,
            'opcoes_tipo_pessoa': opcoes_tipo_pessoa,
            'estados': estados,
            'status_nfe': status_nfe,
            'form': request.POST
        })

@login_required
def monitoramento_nfe(request):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM MonitoramentoNFe ORDER BY Tempo DESC, Empresa")

    rows = cursor.fetchall()
    keys = ('id_nfe', 'pedido', 'ide_nnf', 'status_sefaz', 'data_emissao', 'frg_xml', 'empresa', 'empresa_filial', 'transmitir', 'cce', 'cancelar', 'tempo', 'gnre_nf', 'difal_nf', 'fcp_nf')

    nfes = [dict(zip(keys, row)) for row in rows]
    
    return render(request, 'core/monitoramento-nfe.html', {'nfes': nfes})

@login_required
def nfe_email(request):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM NFe_Email_Erro ORDER BY EmpresaFilial, ide_nNF")
    rows = cursor.fetchall()
    keys = ('id_nfe', 'empresa_filial', 'data_emissao', 'mnemonico', 'status_sefaz', 'pedido', 'ide_nnf', 'dest_email', 'ecfref_mod')

    nfes_erro = [dict(zip(keys, row)) for row in rows]

    cursor.execute("SELECT * FROM NFe_Email_Enviar ORDER BY EmpresaFilial, ide_nNF")
    rows = cursor.fetchall()
    keys = ('id_nfe', 'empresa_filial', 'data_emissao', 'mnemonico', 'status_sefaz', 'pedido', 'ide_nnf', 'dest_email', 'ecfref_mod')

    nfes_enviar = [dict(zip(keys, row)) for row in rows]
    
    return render(request, 'core/nfe-email.html', {'nfes_enviar': nfes_enviar, 'nfes_erro': nfes_erro})

@login_required
def faturados(request):
    empresas = Empresa.objects.all().values('EmpresaFilial', 'Mnemonico').order_by('Mnemonico')

    data_atual = datetime.now().date().strftime('%Y-%m-%d')

    if request.method == 'GET':
        return render(request, 'core/faturados.html', {'empresas': empresas, 'data_atual': data_atual})
    elif request.method == 'POST':
        empresa_filial = request.POST.get('empresa', '')
        str_data_de = request.POST.get('data_de', datetime.now().date().strftime('%Y-%m-%d'))
        str_data_ate = request.POST.get('data_ate', datetime.now().date().strftime('%Y-%m-%d'))

        if str_data_de == '':
            str_data_de = datetime.now().date().strftime('%Y-%m-%d')

        if str_data_ate == '':
            str_data_ate = datetime.now().date().strftime('%Y-%m-%d')

        str_data_de += 'T00:00:00'
        str_data_ate += 'T23:59:59'

        if empresa_filial == '':
            starte_sp = Starte_NFE_400.objects.annotate(empresa=Value('Starte/SP', output_field=CharField())).annotate(empresa_filial=Value(1001, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')
            starte_sc = Starte_SC_NFE_400.objects.annotate(empresa=Value('Starte/SC', output_field=CharField())).annotate(empresa_filial=Value(1002, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')
            starte_mg = Starte_MG_NFE_400.objects.annotate(empresa=Value('Starte/MG', output_field=CharField())).annotate(empresa_filial=Value(1003, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')
            tnl_sp = TNL_NFE_400.objects.annotate(empresa=Value('TNL/SP', output_field=CharField())).annotate(empresa_filial=Value(2001, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')
            tnl_sc = TNL_Blumenau_NFE_400.objects.annotate(empresa=Value('TNL/SC', output_field=CharField())).annotate(empresa_filial=Value(2002, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')
            tnl_pe = TNL_Caruaru_NFE_400.objects.annotate(empresa=Value('TNL/PE', output_field=CharField())).annotate(empresa_filial=Value(2003, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')
            lanmaxlog = LanmaxLog_NFE_400.objects.annotate(empresa=Value('LanmaxLog', output_field=CharField())).annotate(empresa_filial=Value(7001, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')
            maxipecas = Maxipecas_NFE_400.objects.annotate(empresa=Value('Maxipeças', output_field=CharField())).annotate(empresa_filial=Value(4001, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')
            maxipecas_filial = Maxipecas_Filial_NFE_400.objects.annotate(empresa=Value('Maxipeças/Filial', output_field=CharField())).annotate(empresa_filial=Value(4002, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')
            lanmaxpecas = LanmaxPecas_NFE_400.objects.annotate(empresa=Value('LP/SP', output_field=CharField())).annotate(empresa_filial=Value(5001, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')
            lpblumenau = LPBlumenau_NFE_400.objects.annotate(empresa=Value('LP/SC', output_field=CharField())).annotate(empresa_filial=Value(5002, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')
            portoreal = PortoReal_NFE_400.objects.annotate(empresa=Value('PortoReal', output_field=CharField())).annotate(empresa_filial=Value(5501, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')
            infinity = Infinity_NFE_400.objects.annotate(empresa=Value('Infinity', output_field=CharField())).annotate(empresa_filial=Value(6100, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')
            vialuna = Vialuna_NFE_400.objects.annotate(empresa=Value('Vialuna', output_field=CharField())).annotate(empresa_filial=Value(6001, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')
            liberty_pe = Liberty_NFE_400.objects.annotate(empresa=Value('Liberty/PE', output_field=CharField())).annotate(empresa_filial=Value(2800, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')
            liberty_ce = Liberty_CE_NFE_400.objects.annotate(empresa=Value('Liberty/CE', output_field=CharField())).annotate(empresa_filial=Value(2801, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')
            greenmotor_sp = GreenMotor_NFE_400.objects.annotate(empresa=Value('GreenMotor/SP', output_field=CharField())).annotate(empresa_filial=Value(-3101, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')
            greenmotor_sc = GreenMotor_SC_NFE_400.objects.annotate(empresa=Value('GreenMotor/SC', output_field=CharField())).annotate(empresa_filial=Value(-3102, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')
            rio_ba = Rio_BA_NFE_400.objects.annotate(empresa=Value('Rio/BA', output_field=CharField())).annotate(empresa_filial=Value(8001, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')
            rio_mg = Rio_MG_NFE_400.objects.annotate(empresa=Value('Rio/MG', output_field=CharField())).annotate(empresa_filial=Value(8005, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')
            rio_mt = Rio_MT_NFE_400.objects.annotate(empresa=Value('Rio/MT', output_field=CharField())).annotate(empresa_filial=Value(8007, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')
            rio_pr = Rio_PR_NFE_400.objects.annotate(empresa=Value('Rio/PR', output_field=CharField())).annotate(empresa_filial=Value(8004, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')
            rio_rj = Rio_RJ_NFE_400.objects.annotate(empresa=Value('Rio/RJ', output_field=CharField())).annotate(empresa_filial=Value(8006, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')
            rio_rs = Rio_RS_NFE_400.objects.annotate(empresa=Value('Rio/RS', output_field=CharField())).annotate(empresa_filial=Value(8003, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF')

            faturamento = starte_sp.union(
                starte_sc,
                starte_mg,
                tnl_sp,
                tnl_sc,
                tnl_pe,
                lanmaxlog,
                maxipecas,
                maxipecas_filial,
                lanmaxpecas,
                lpblumenau,
                portoreal,
                infinity,
                vialuna,
                liberty_pe,
                liberty_ce,
                greenmotor_sp,
                greenmotor_sc,
                rio_ba,
                rio_mg,
                rio_mt,
                rio_pr,
                rio_rj,
                rio_rs
            ).order_by('-dhRecbto')

            return render(request, 'core/faturados.html', {'empresas': empresas, 'faturamento': faturamento, 'data_atual': data_atual})

        try:
            empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
            nome_tabela = apps.get_model('core', empresa.Tabela)
        except Empresa.DoesNotExist:
            messages.error(request, 'Empresa não encontrada!')
            return redirect('core_faturados')
        
        if int(empresa_filial) in empresas_greenmotor:
            pedidos = list(Pedido.objects.using('greenmotor').filter(empresa_filial=empresa_filial, cod_pedido__gte=2400000).values_list('cod_pedido', flat=True))
            queryset = nome_tabela.objects.filter(Pedido__in=pedidos)
        else:
            pedidos = list(Pedido.objects.using('lanmax').filter(empresa_filial=empresa_filial, cod_pedido__gte=202400000).values_list('cod_pedido', flat=True))
            queryset = nome_tabela.objects.filter(Pedido__in=pedidos)
    
        faturamento = queryset.annotate(empresa=Value(empresa.Mnemonico, output_field=CharField())).annotate(empresa_filial=Value(empresa.EmpresaFilial, output_field=IntegerField())).filter(dhRecbto__range=(str_data_de, str_data_ate)).values('id_nfe', 'empresa_filial', 'empresa', 'dhRecbto', 'status_sefaz', 'Pedido', 'ide_nNF', 'TotalICMS_vNF').order_by('-dhRecbto')

        if len(faturamento) == 0:
            messages.error(request, 'Sem faturamento nesta data!')
            return redirect('core_faturados')
        else:
            return render(request, 'core/faturados.html', {'empresas': empresas, 'faturamento': faturamento, 'data_atual': data_atual})

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