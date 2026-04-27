from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.apps import apps
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from core.models import *
from lanmax.models import *
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from .reports import *
from pathlib import Path
from nfe_util_2g.utils import *
from datetime import datetime, time
from io import BytesIO
import shutil, requests, os, win32api, win32print
from .pix import *
from email_validator import validate_email, EmailNotValidError
from rest_framework.decorators import api_view
from celery import shared_task

empresas_greenmotor = [-3102, -3101, -2003, -2002, -2001, -1033, -1003, -1002, -1001, 8001, 8003, 8004, 8005, 8006, 8007]

@api_view(['GET'])
def gerar_orcamento_pdf(request, cod_pedido):
    try:
        if int(cod_pedido) < 100000000 and int(cod_pedido) > 0:
            pedido = Pedido.objects.using('greenmotor').get(cod_pedido=cod_pedido)
        else:
            pedido = Pedido.objects.using('lanmax').get(cod_pedido=cod_pedido)
    except Pedido.DoesNotExist:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Pedido não encontrado!'})
    
    cursor = connection.cursor()

    if int(pedido.cod_pedido) < 100000000 and int(pedido.cod_pedido) > 0:
        cursor.execute('EXEC GreenMotor.dbo.Pedido_Orcamento %s, %s', [pedido.cod_pedido, 0])
    else:
        cursor.execute('EXEC Lanmax.dbo.Pedido_Orcamento %s, %s', [pedido.cod_pedido, 0])

    rows = cursor.fetchall()
    rows_ordenados = sorted(rows, key=lambda x: x[4])

    keys = ('cod_pedido', 'func_comissao', 'valor_total', 'observacoes', 'nome_prod', 'descricao', 
            'quantidade', 'valor_unit_ref', 'valor_unit_prom', 'valor_item_ref', 'valor_item_prom', 'aliq_ipi',
            'nome', 'razao_social', 'cnpj', 'inscricao_estadual', 'nome_contato', 'cargo_contato', 'logradouro',
            'numero', 'bairro', 'municipio', 'estado', 'cep', 'telefone', 'telefone2', 'celular', 'email', 
            'mnemonico', 'total_icms_st', 'e_razao_social', 'e_endereco', 'e_cep', 'e_cnpj', 'e_contato', 
            'valor_unit_st', 'total_ipi', 'nacional', 'transportadora', )
    
    orcamentos = [dict(zip(keys, row)) for row in rows_ordenados]

    if int(pedido.cod_pedido) < 100000000 and int(pedido.cod_pedido) > 0:
        cursor.execute('SELECT CodPedido, Vencimento, NumParcela, Valor_, Forma, Status, DataDeposito, Obs FROM GreenMotor.dbo.Pagamentos Where CodPedido = %s ORDER BY Vencimento', [pedido.cod_pedido, ])
    else:
        cursor.execute('SELECT CodPedido, Vencimento, NumParcela, Valor_, Forma, Status, DataDeposito, Obs FROM Lanmax.dbo.Pagamentos Where CodPedido = %s ORDER BY Vencimento', [pedido.cod_pedido, ])
    
    rows = cursor.fetchall()
    keys = ('cod_pedido', 'vencimento', 'num_parcela', 'valor', 'forma', 'status', 'data_deposito', 'obs')

    pagamentos = [dict(zip(keys, row)) for row in rows]

    caminho_pdf = gerar_pdf_orcamento(request, orcamentos, pagamentos, pedido.cod_pedido)
    caminho_anexo = '\\\\192.168.10.235\\Database\\Anexos\\'

    if Path(caminho_pdf).exists():
        shutil.copy(caminho_pdf, caminho_anexo)
        return JsonResponse({'erro': False, 'mensagem': 'Orçamento PDF gerado com sucesso!'})
    else:
        return JsonResponse({'erro': True, 'mensagem': 'Ocorreu um erro ao gerar o Orçamento PDF!'})

@login_required
def consulta_status(request, cod_empresa):
    try:
        empresa = Empresa.objects.get(EmpresaFilial=cod_empresa)
    except Empresa.DoesNotExist:
        return JsonResponse({'erro': True, 'status': -1, 'mensagem': 'Empresa inexistente!'})

    try:
        status = consulta_status_2g(empresa)
        return JsonResponse({'erro': False, 'status': status[0], 'titulo': 'Status SEFAZ/'+empresa.emit_UF, 'mensagem': status[3]})
    except:
        return JsonResponse({'erro': True, 'status': -1, 'titulo': '', 'mensagem': 'Erro!'})

@login_required
def notas_fiscais(request, cod_empresa=None):
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')

    columns = ['Pedido', 'ide_nNF', 'status_sefaz', 'ide_serie', 'dtp', 'dest_xNome']
    order_column_index = int(request.GET.get("order[0][column]", 5))
    order_column = columns[order_column_index]
    order_dir = request.GET.get("order[0][dir]", "desc")

    if order_dir == "desc":
        order_column = f"-{order_column}"

    filtro_pedido = request.GET.get('pedido', '')
    filtro_nfe = request.GET.get('nfe', '').strip()
    filtro_status = request.GET.get('status', '').strip()

    if cod_empresa:
        try:
            empresa = Empresa.objects.get(EmpresaFilial=cod_empresa)
        except Empresa.DoesNotExist:
            return JsonResponse('Empresa inexistente!')

        modelo_nfe = apps.get_model('core', empresa.Tabela)

        if int(cod_empresa) in empresas_greenmotor:
            pedidos = list(Pedido.objects.using('greenmotor').filter(empresa_filial=cod_empresa, cod_pedido__gte=2400000).values_list('cod_pedido', flat=True))
            queryset = modelo_nfe.objects.filter(Pedido__in=pedidos)
        else:
            pedidos = list(Pedido.objects.using('lanmax').filter(empresa_filial=cod_empresa, cod_pedido__gte=202400000).values_list('cod_pedido', flat=True))
            queryset = modelo_nfe.objects.filter(Pedido__in=pedidos)

        if filtro_pedido:
            queryset = queryset.filter(Pedido=filtro_pedido)

        if filtro_nfe:
            queryset = queryset.filter(ide_nNF__icontains=filtro_nfe)

        if filtro_status:
            queryset = queryset.filter(status_sefaz=filtro_status)

        total_filtrado = queryset.count()
        queryset = queryset.order_by(order_column)[start:start+length]

        data = [
            {
                'id_nfe': nfe.id_nfe,
                'Pedido': nfe.Pedido,
                'ide_nNF': nfe.ide_nNF.strip() if nfe.ide_nNF else '0',
                'ide_serie': nfe.ide_serie if nfe.ide_serie != 0 else 'COB',
                'status_sefaz': nfe.status_sefaz.strip() if nfe.status_sefaz else 'NFe não enviada',
                'dtp': nfe.dtp.strftime('%d/%m/%Y %H:%M:%S') if nfe.dtp else '',
                'dest_xNome': nfe.dest_xNome.strip() if nfe.dest_xNome else ''
            } for nfe in queryset
        ]

        response = {
            'draw': draw,
            'recordsTotal': modelo_nfe.objects.count(),
            'recordsFiltered': total_filtrado,
            'data': data
        }
    else:
        response = {
            'draw': draw,
            'recordsTotal': 0,
            'recorsFiltered': 0,
            'data': []
        }

    return JsonResponse(response)

@login_required
def status_disponiveis(request, cod_empresa=None):
    if cod_empresa:
        try:
            empresa = Empresa.objects.get(EmpresaFilial=cod_empresa)
        except Empresa.DoesNotExist:
            return JsonResponse('Empresa inexistente!')

        modelo_nfe = apps.get_model('core', empresa.Tabela)
        status = list(modelo_nfe.objects.all().values('status_sefaz').distinct().order_by('status_sefaz'))
    else:
        status = []

    return JsonResponse({'status_disponiveis': status})

@login_required
def consulta_empresa(request, cod_pedido):
    if cod_pedido < 100000000:
        pedido_empresa = Pedido.objects.using('greenmotor').filter(cod_pedido=cod_pedido).values('empresa_filial').first()
    else:
        pedido_empresa = Pedido.objects.using('lanmax').filter(cod_pedido=cod_pedido).values('empresa_filial').first()

    return JsonResponse(pedido_empresa, safe=False)

# @api_view(['GET'])
def gerar_danfe(request, empresa_filial, id_nfe):
    try:
        empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
        nome_tabela = apps.get_model('core', empresa.Tabela)
        nome_tabela_itens = apps.get_model('core', empresa.TabelaItens)
    except Empresa.DoesNotExist:
        return JsonResponse({'erro': True, 'mensagem': 'Empresa não encontrada!'})

    try:
        nfe = nome_tabela.objects.get(id_nfe=id_nfe)
    except nome_tabela.DoesNotExist:
        return JsonResponse({'erro': True, 'mensagem': 'Nota Fiscal não encontrada!'})

    nfe_itens = nome_tabela_itens.objects.filter(id_nfe=nfe.id_nfe).order_by('id_item')
    diretorio = Diretorio.objects.filter(CNPJ=empresa.emit_CNPJ, TipoArquivo='xmlAutorizado').first()
    xml_autorizado = Path(diretorio.Diretorio + nfe.ide_nNF + '-procNFe.xml')

    if 'Lote' in nfe.status_sefaz or nfe.status_sefaz == 'NFe não enviada':
        return JsonResponse({'erro': True, 'mensagem': 'Nota Fiscal não foi emitida!'})

    if not nfe_itens:
        return JsonResponse({'erro': True, 'mensagem': 'Itens da Nota Fiscal não encontrada!'})

    if not xml_autorizado.exists():
        return JsonResponse({'erro': True, 'mensagem': 'Arquivo XML Autorizado não encontrado!'})

    boletos = []

    if nfe.ide_idDest != 3:
        with connection.cursor() as cursor:
            if int(nfe.Pedido) <= 9999999:
                cursor.execute(
                    "SELECT Vencimento, Valor_ FROM GreenMotor.dbo.Pagamentos WHERE CodPedido = %s AND Forma = %s AND Conta NOT LIKE %s AND CONTA NOT LIKE %s AND Status IS NULL ORDER BY Vencimento",
                    [nfe.Pedido, 'BOL', '%-Rio%', 'Ometz%']
                )
            else:
                cursor.execute(
                    "SELECT Vencimento, Valor_ FROM Lanmax.dbo.Pagamentos WHERE CodPedido = %s AND Forma = %s AND Conta NOT LIKE %s AND CONTA NOT LIKE %s AND Status IS NULL ORDER BY Vencimento",
                    [nfe.Pedido, 'BOL', '%Rio%', 'Ometz%']
                )

            rows = cursor.fetchall()
            keys = ('vencimento', 'valor')

            for row in rows:
                boletos.append(dict(zip(keys, row)))

    pdf = gerar_pdf_danfe(empresa, nfe, nfe_itens, list(boletos))
    caminho_pdf = Path(pdf)

    if caminho_pdf.exists():
        diretorio = Diretorio.objects.filter(CNPJ=empresa.emit_CNPJ, TipoArquivo='pdfDANFe').first()
        
        # Copia para a pasta DANFE PDF da empresa correspondente
        if Path(diretorio.Diretorio).is_dir():
            if not Path(diretorio.Diretorio + nfe.ide_nNF + '-danfe.pdf').exists():
                shutil.copy(caminho_pdf, diretorio.Diretorio)
        else:
            return JsonResponse({'erro': True, 'mensagem': 'Pasta da DANFE não encontrada!'})

        caminho_nfe = get_path_repo(nfe, empresa)

        if not Path(caminho_nfe).is_dir():
            Path(caminho_nfe).mkdir(parents=True, exist_ok=True)

        # Copia para a pasta REPOSITORIO da empresa correspondente
        if Path(caminho_nfe).is_dir():
            if not Path(caminho_nfe + nfe.ide_nNF + '-danfe.pdf').exists():
                shutil.copy(caminho_pdf, caminho_nfe + nfe.ide_nNF + '-danfe.pdf')
        else:
            Path(caminho_nfe).mkdir(parents=True, exist_ok=True)
            return JsonResponse({'erro': True, 'mensagem': 'Pasta da NF-e não encontrada!'})
        
        # impressora = ''

        # win32api.ShellExecute(
        #     0,
        #     'printto',
        #     caminho_pdf,
        #     f'"{impressora}"',
        #     '.',
        #     0
        # )

        caminho_pdf.unlink(missing_ok=True)
        return JsonResponse({'erro': False, 'mensagem': f'DANFE gerada com sucesso!'})
    else:
        return JsonResponse({'erro': True, 'mensagem': 'Erro ao gerar a DANFE!'})

    # response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = f'inline; filename="danfe_{nfe.ide_nNF}.pdf"'
    # response.write(pdf)
    # return response

# @api_view(['GET'])
@xframe_options_exempt
def gerar_boleto(request, empresa_filial, id_nfe):
    try:
        empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
        nome_tabela = apps.get_model('core', empresa.Tabela)
    except Empresa.DoesNotExist:
        return JsonResponse({'erro': True, 'mensagem': 'Empresa não encontrada!'})

    try:
        nfe = nome_tabela.objects.get(id_nfe=id_nfe)
    except nome_tabela.DoesNotExist:
        return JsonResponse({'erro': True, 'mensagem': 'Nota Fiscal não encontrada!'})

    cursor = connection.cursor()

    if int(nfe.Pedido) < 100000000 and int(nfe.Pedido) > 0:
        if isEmpRio(empresa):
            if temBol(nfe, empresa):
                cursor.execute("SELECT * FROM GreenMotor.dbo.boletos WHERE CodPedido = %s AND Conta NOT LIKE %s ORDER BY NossoNum", [nfe.Pedido, 'Ometz%',])
            else:
                return JsonResponse({'erro': True, 'mensagem': 'Pedido sem boleto!'})
        else:
            if temBolSemRio(nfe, empresa):
                cursor.execute("SELECT * FROM GreenMotor.dbo.boletos WHERE CodPedido = %s AND Conta NOT LIKE %s AND Conta NOT LIKE %s ORDER BY NossoNum", [nfe.Pedido, '%Rio%', 'Ometz%',])
            else:
                return JsonResponse({'erro': True, 'mensagem': 'Pedido sem boleto!'})
    else:
        if temBolSemRio(nfe, empresa):
            cursor.execute("SELECT * FROM Lanmax.dbo.boletos WHERE CodPedido = %s AND Conta NOT LIKE %s AND Conta NOT LIKE %s ORDER BY NossoNum", [nfe.Pedido, '%Rio%', 'Ometz%',])
        else:
            return JsonResponse({'erro': True, 'mensagem': 'Pedido sem boleto!'})

    rows = cursor.fetchall()
    keys = (
        'beneficiario', 'cnpj_benef', 'cod_pedido', 'razao_social', 'endereco', 'cid_est', 'cep', 'cnpj', 'vencimento', 'valor', 'conta', 'ag', 'cc', 'digito', 'carteira',
        'nosso_num', 'data_pedido', 'num_doc', 'agencia_conta', 'controle_interno', 'gerar_qrcode', 'endereco2', 'bairro', 'cidade', 'estado', 'num_parcela', 'id_location'
    )
    boletos = []

    for row in rows:
        boletos.append(dict(zip(keys, row)))

    if len(boletos) == 0:
        return JsonResponse({'erro': True, 'arquivo': None, 'mensagem': 'Pedido sem boleto ou sem Nosso Número gerado ou já foram pagos!'})
    
    pasta_repo = get_path_repo(nfe, empresa)

    if not Path(pasta_repo).is_dir():
        Path(pasta_repo).mkdir(parents=True, exist_ok=True)

    nome_boleto = pasta_repo + 'boletos_' + nfe.ide_nNF + '.pdf'

    c = canvas.Canvas(nome_boleto, pagesize=A4)
    c.setTitle(f'Boleto {nfe.ide_nNF}')

    # path_bolecode = Constante.objects.using('lanmax').get(CodConst=207)

    for boleto in boletos:
        # QRCode Bolecode
        #  qrcode_bolecode = f'{path_bolecode.Constante}bolecode_{boleto['cod_pedido']}_{boleto['nosso_num']}.jpg'
        # status_bolecode = 0

        # if not Path(qrcode_bolecode).exists():
        #     status_bolecode = gerar_bolecode(boleto['cod_pedido'], boleto['nosso_num'])

        #     if status_bolecode != 200:
        #         return JsonResponse({'erro': True, 'arquivo': None, 'mensagem': 'Ocorreu um erro ao gerar QRCode PIX!'})

        desenhar_parcela_boleto(c, boleto)
        c.showPage()

    c.save()

    # pasta_boletos = os.path.join(settings.BASE_DIR, 'static', 'boletos')
    # nome_boleto = os.path.join(pasta_boletos, f'boleto_{nfe.ide_nNF}.pdf')

    # shutil.copy(nome_arquivo, nome_boleto)

    with open(nome_boleto, "rb") as f:
        buffer = BytesIO(f.read())

    # return JsonResponse({'erro': False, 'arquivo': nome_arquivo, 'mensagem': 'Boleto gerado com sucesso!'})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{nome_boleto}"'
    response.write(buffer.getvalue())
    return response

@csrf_exempt
def gerar_pix(request):
    if request.method != 'POST':
        return JsonResponse({'erro': True, 'mensagem': 'Método de requisição inválido!'})

    cod_pedido = int(request.POST.get('pedido'))
    num_parcela = request.POST.get('parcela')
    valor = request.POST.get('valor')

    cursor = connection.cursor()

    if cod_pedido <= 9999999:
        cursor.execute(
            "SELECT c.RazaoSocial, c.CNPJ, pa.Vencimento, pa.Conta FROM GreenMotor.dbo.Pagamentos pa INNER JOIN GreenMotor.dbo.Pedidos p ON pa.CodPedido = p.CodPedido " \
            "INNER JOIN GreenMotor.dbo.Clientes c ON p.CodCliente = c.CodCliente " \
            "WHERE (StatusPed = %s OR StatusPed LIKE %s) AND pa.CodPedido = %s AND NumParcela = %s AND Forma = %s AND Status IS NULL",
            ['Inicial', 'Pend%', cod_pedido, num_parcela, 'Pix',]
        )

        txid = f'{str(cod_pedido)}{uuid.uuid4().hex[:28].upper()}'
    else:
        cursor.execute(
            "SELECT c.RazaoSocial, c.CNPJ, pa.Vencimento, pa.Conta FROM Lanmax.dbo.Pagamentos pa INNER JOIN Lanmax.dbo.Pedidos p ON pa.CodPedido = p.CodPedido " \
            "INNER JOIN Lanmax.dbo.Clientes c ON p.CodCliente = c.CodCliente " \
            "WHERE (StatusPed = %s OR StatusPed LIKE %s) AND pa.CodPedido = %s AND NumParcela = %s AND Forma = %s AND Status IS NULL",
            ['Inicial', 'Pend%', cod_pedido, num_parcela, 'Pix',]
        )

        txid = f'{str(cod_pedido)}{uuid.uuid4().hex[:26].upper()}'

    result = cursor.fetchone()

    if not result:
        return JsonResponse({'erro': True, 'mensagem': 'Título PIX não encontrado!'})

    keys = ('razao_social', 'cnpj', 'vencimento', 'conta')
    titulo_pix = dict(zip(keys, result))

    conta_lanmax = Conta.objects.using('lanmax').get(Conta=titulo_pix.get('conta'))
    empresa_filial = EmpresaFilial.objects.using('lanmax').get(empresa_filial=conta_lanmax.Empresa)
    url = "https://secure.api.itau/pix_recebimentos/v2/cob/" + txid
    token_itau = get_token_itau(conta_lanmax.Empresa)

    if not token_itau:
        return JsonResponse({'erro': True, 'mensagem': 'Token Itaú não foi gerado!'})
    
    print(titulo_pix.get('vencimento').date())

    vencimento = datetime.combine(titulo_pix.get('vencimento').date(), time(23, 59, 59))
    diferenca = vencimento - datetime.now()
    expiracao = int(diferenca.total_seconds())

    cgc_devedor = str(titulo_pix.get('cnpj')).zfill(14) if len(str(titulo_pix.get('cnpj'))) > 11 else str(titulo_pix.get('cnpj')).zfill(11)
    strjson_cgc_devedor = '"cnpj": "'+cgc_devedor+'",' if len(cgc_devedor) > 11 else '"cpf": "'+cgc_devedor+'",'

    headers = {
        'x-itau-apikey': '96decebf-5c47-4410-95bf-0c4b803e4bb2',
        'x-itau-correlationID': 'bc4d8712-904a-47af-a3a0-63751ddb7e56',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token_itau
    }

    data = '{' \
        '"calendario": {"expiracao": "'+str(expiracao)+'"},' \
        '"devedor": {' + strjson_cgc_devedor + '"nome": "'+titulo_pix.get('razao_social')+'"},' \
        '"valor": {"original": "'+str(valor)+'"},' \
        '"chave": "'+empresa_filial.cnpj+'"' \
    '}'

    print(data)

    r = requests.put(url, data=data, headers=headers, cert=(conta_lanmax.caminho_arquivo_crt, conta_lanmax.caminho_arquivo_key))

    print(data, r.status_code, r.text)

    if r.status_code == 201:
        pix_json = json.loads(r.text)
        pasta_pix = os.path.join(settings.BASE_DIR, 'static', 'pix')
        arquivo_pix = os.path.join(pasta_pix, f'pix_{cod_pedido}_{datetime.now().strftime('%d%m%Y_%H%M%S')}.txt')

        with open(arquivo_pix, 'w', encoding='utf-8') as f:
            f.write(r.text)
        
        if cod_pedido <= 9999999:
            cursor.execute(
                'UPDATE GreenMotor.dbo.Pagamentos SET txid = %s, pixCopiaECola = %s WHERE CodPedido = %s AND NumParcela = %s AND Forma = %s',
                [pix_json.get('txid'), pix_json.get('pixCopiaECola'), cod_pedido, num_parcela, 'PIX']
            )
        else:
            cursor.execute(
                'UPDATE Lanmax.dbo.Pagamentos SET txid = %s, pixCopiaECola = %s WHERE CodPedido = %s AND NumParcela = %s AND Forma = %s',
                [pix_json.get('txid'), pix_json.get('pixCopiaECola'), cod_pedido, num_parcela, 'PIX']
            )

        connection.commit()

        return JsonResponse({'erro': False, 'mensagem': 'PIX gerado com sucesso!'})

    return JsonResponse({'erro': True, 'mensagem': 'Ocorreu um erro ao gerar a chave PIX.'})

@csrf_exempt
def consulta_pix(request, conta, inicio, fim):
    conta_lanmax = Conta.objects.using('lanmax').get(Conta=conta)
    empresa = EmpresaFilial.objects.using('lanmax').get(empresa_filial=conta_lanmax.Empresa)
    id_conta = f'60701190{str(conta_lanmax.Ag).zfill(4)}{str(conta_lanmax.CC).zfill(13)}'
    url = f"https://secure.api.itau/pix_recebimentos/v2/pix?inicio={inicio}&fim={fim}"
    token_itau = get_token_itau(conta_lanmax.Empresa)

    headers = {
        # 'x-itau-correlationID': 'bc4d8712-904a-47af-a3a0-63751ddb7e56',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token_itau
    }

    r = requests.get(url, headers=headers, cert=(conta_lanmax.caminho_arquivo_crt, conta_lanmax.caminho_arquivo_key))

    print(r.status_code, r.text)

    if r.status_code == 200:
        with open('C:\\Users\\rmizukosi.GRUPOLANMAX\\Desktop\\consulta.txt', 'w', encoding='utf-8') as f:
            f.write(r.text)

        return JsonResponse({'erro': False, 'mensagem': 'Sucesso!'})

@csrf_exempt
def cancelar_pix(request):
    cancelar_chave_pix()
    # consulta_pix_by_id()
    return JsonResponse({'erro': False, 'mensagem': 'Sucesso!'})

@api_view(['POST'])
@csrf_exempt
def transmitir_nfce(request):
    if request.method != 'POST':
        return JsonResponse({'erro': True, 'mensagem': 'Método de requisição inválido!'})

    id_nfe = int(request.POST.get('id'))
    empresa_filial = int(request.POST.get('empresa'))

    try:
        empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
        nome_tabela = apps.get_model('core', empresa.Tabela)
        nome_tabela_itens = apps.get_model('core', empresa.TabelaItens)
    except Empresa.DoesNotExist:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Empresa não encontrada!'})

    try:
        nfe = nome_tabela.objects.get(id_nfe=id_nfe)
    except nome_tabela.DoesNotExist:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Nota Fiscal não encontrada!'})
    
    if controleInterno(int(nfe.Pedido)):
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Pedido é Controle Interno!'})
    
    if nfe.ide_mod != 65:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Modelo da NF-e diferente de 65!'})
    
    if 'Aut' in nfe.status_sefaz or 'Carta' in nfe.status_sefaz or 'Canc' in nfe.status_sefaz:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'NFC-e já foi emitida!'})
    
    try:
        nfe_itens = nome_tabela_itens.objects.filter(id_nfe=id_nfe).order_by('id_item')
    except nome_tabela_itens.DoesNotExist:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Itens da Nota Fiscal não encontrada!'})
    
    cursor = connection.cursor()

    if int(nfe.Pedido) < 100000000 and int(nfe.Pedido) > 0:
        cursor.execute('EXEC dbo.ajustaVencto_GM %s', [int(nfe.Pedido),])
    elif int(nfe.Pedido) >= 100000000:
        cursor.execute('EXEC dbo.ajustaVencto %s', [int(nfe.Pedido),])

    result = cursor.fetchone()
        
    if result[0] != 0:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': result[1]})
    
    nfe.Transmitir = True
    nfe.DataEmissao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    nfe.save()
    nfe.refresh_from_db()
    
    status_chave_acesso = gera_chave_acesso(nfe, empresa)

    if status_chave_acesso == 5601:
        gera_xml(nfe, nfe_itens, empresa)
        assina_nfce(nfe, empresa)
        status_retorno, msg_retorno = envia_nfe_sincrono(nfe, empresa)

        if status_retorno == 100:
            gera_qrcode(nfe, empresa)

            cursor.execute('SELECT fp.Descricao,f.pagamento_vPag FROM FormasPagto_NFE f INNER JOIN FormasPagto fp ON f.pagamento_tPag = fp.Codigo WHERE id_nfe = %s AND ide_serie = %s ORDER BY f.pagamento_nForma', [nfe.id_nfe, nfe.ide_serie,])

            rows = cursor.fetchall()

            keys = ('descricao', 'valor')
            formas_pagto = []

            for row in rows:
                formas_pagto.append(dict(zip(keys, row)))
            
            pasta_cupons = os.path.join(settings.BASE_DIR, 'static', 'relatorios')
            nome_cupom_static = os.path.join(pasta_cupons, f'cupom_{nfe.ide_nNF}.pdf')
            nome_cupom = get_path_repo(nfe, empresa) + f'cupom_{nfe.ide_nNF}.pdf'

            desenhar_cupom(empresa, nfe, nfe_itens, formas_pagto)

            if Path(nome_cupom_static).is_file():
                shutil.copy(nome_cupom_static, nome_cupom)
            #     impressora = ''

            #     win32api.ShellExecute(
            #         0,
            #         'printto',
            #         nome_cupom,
            #         f'"{impressora}"',
            #         '.',
            #         0
            #     )

                return JsonResponse({'erro': False, 'status': 100, 'mensagem': 'Baixa do pedido no sistema realizado com sucesso!'})
            else:
                return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Cupom não foi gerado!'})

            # return JsonResponse({'erro': False, 'status': 100, 'mensagem': 'Baixa do pedido no sistema realizado com sucesso!'})
        else:
            nfe.frg_xml = msg_retorno
            nfe.status_sefaz = 'Lote recebido com sucesso'
            # nfe.XML_Transmitido = True
            nfe.save()
            nfe.refresh_from_db()
            return JsonResponse({'erro': True, 'status': status_retorno, 'mensagem': msg_retorno})
    else:
        return JsonResponse({'erro': True, 'status': status_chave_acesso, 'mensagem': 'Erro ao gerar a chave de acesso!'})

@api_view(['POST'])
#@shared_task
@csrf_exempt
def transmitir_nfe(request):
    if request.method != 'POST':
        return JsonResponse({'erro': True, 'mensagem': 'Método de requisição inválido!'})

    id_nfe = int(request.POST.get('id'))
    empresa_filial = int(request.POST.get('empresa'))

    try:
        empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
        nome_tabela = apps.get_model('core', empresa.Tabela)
        nome_tabela_itens = apps.get_model('core', empresa.TabelaItens)
    except Empresa.DoesNotExist:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Empresa não encontrada!'})

    try:
        nfe = nome_tabela.objects.get(id_nfe=id_nfe)
    except nome_tabela.DoesNotExist:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Nota Fiscal não encontrada!'})
    
    if controleInterno(int(nfe.Pedido)):
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Pedido é Controle Interno!'})
    
    if nfe.ide_mod != 55:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Modelo da NF-e diferente de 55!'})
    
    if 'Aut' in nfe.status_sefaz or 'Carta' in nfe.status_sefaz or 'Canc' in nfe.status_sefaz:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'NF-e já foi emitida!'})
    
    try:
        nfe_itens = nome_tabela_itens.objects.filter(id_nfe=id_nfe).order_by('id_item')
    except nome_tabela_itens.DoesNotExist:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Itens da Nota Fiscal não encontrada!'})
    
    cursor = connection.cursor()

    if int(nfe.Pedido) >= 100000000:
        cursor.execute('SELECT dbo.ValidaRegistrador(%s)', [nfe.Pedido, ])
        result = cursor.fetchone()
        
        if result[0] != '':
            return JsonResponse({'erro': True, 'status': 0, 'mensagem': result[0]})
        
        cursor.execute('SELECT dbo.ValidaPedVinculados(%s)', [nfe.Pedido,])
        result = cursor.fetchone()

        if result[0] != '':
            return JsonResponse({'erro': True, 'status': 0, 'mensagem': result[0]})
    
    if int(nfe.Pedido) < 100000000 and int(nfe.Pedido) > 0:
        cursor.execute('EXEC dbo.ajustaVencto_GM %s', [int(nfe.Pedido),])

        result = cursor.fetchone()
        
        if result[0] != 0:
            return JsonResponse({'erro': True, 'status': 0, 'mensagem': result[1]})
    elif int(nfe.Pedido) >= 100000000:
        cursor.execute('EXEC dbo.ajustaVencto %s', [int(nfe.Pedido),])

        result = cursor.fetchone()
        
        if result[0] != 0:
            return JsonResponse({'erro': True, 'status': 0, 'mensagem': result[1]})

    nfe.Transmitir = True
    nfe.DataEmissao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    nfe.save()
    nfe.refresh_from_db()
    
    status_chave_acesso = gera_chave_acesso(nfe, empresa)
    gnre = False
    difal = False
    fcp = False
    boleto = False

    if status_chave_acesso == 5601:
        gera_xml(nfe, nfe_itens, empresa)
        status_retorno, msg_retorno = envia_nfe_sincrono(nfe, empresa)

        if status_retorno == 100:
            if tem_gnre(id_nfe, empresa.ide_serie):
                gnre = True

            if gera_difal(id_nfe, empresa.ide_serie):
                difal = True

            if gera_fcp(id_nfe, empresa.ide_serie):
                fcp = True

            gerar_danfe(request, empresa_filial, id_nfe)

            if temBol(nfe, empresa):
                gerar_boleto(request, empresa_filial, id_nfe)
                boleto = True

            return JsonResponse({'erro': False, 'tem_boleto': boleto, 'tem_gnre': gnre, 'tem_difal': difal, 'tem_fcp': fcp, 'status': status_retorno, 'mensagem': 'Baixa do pedido no sistema realizado com sucesso!'})
        else:
            nfe.frg_xml = msg_retorno
            # nfe.status_sefaz = 'Lote recebido com sucesso'
            # nfe.XML_Transmitido = True
            nfe.save()
            nfe.refresh_from_db()
            return JsonResponse({'erro': True, 'status': status_retorno, 'mensagem': msg_retorno})
    else:
        return JsonResponse({'erro': True, 'status': status_chave_acesso, 'mensagem': 'Erro ao gerar a chave de acesso!'})

def tem_boleto(request, empresa_filial, id_nfe):
    try:
        empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
        nome_tabela = apps.get_model('core', empresa.Tabela)
    except Empresa.DoesNotExist:
        return JsonResponse({'erro': True, 'mensagem': 'Empresa não encontrada!'})

    try:
        nfe = nome_tabela.objects.get(id_nfe=id_nfe)
    except nome_tabela.DoesNotExist:
        return JsonResponse({'erro': True, 'mensagem': 'Nota Fiscal não encontrada!'})
    
    if temBol(nfe, empresa):
        return JsonResponse({'erro': False, 'tem_bol': True, 'mensagem': 'Tem boleto'})
    else:
        return JsonResponse({'erro': False, 'tem_bol': False, 'mensagem': 'Não tem boleto'})

@api_view(['POST'])
@csrf_exempt
def carta_correcao(request):
    if request.method != 'POST':
        return JsonResponse({'erro': True, 'mensagem': 'Método de requisição inválido!'})

    id_nfe = int(request.POST.get('id'))
    empresa_filial = int(request.POST.get('empresa'))
    justificativa = request.POST.get('justificativa')

    try:
        empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
        nome_tabela = apps.get_model('core', empresa.Tabela)
    except Empresa.DoesNotExist:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Empresa não encontrada!'})

    try:
        nfe = nome_tabela.objects.get(id_nfe=id_nfe)
    except nome_tabela.DoesNotExist:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Nota Fiscal não encontrada!'})
    
    if 'Aut' not in nfe.status_sefaz and 'Carta' not in nfe.status_sefaz:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'NF-e não está como Autorizada!'})
    
    if nfe.nSeqEvento:
        if int(nfe.nSeqEvento) > 20:
            return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Número de CCe atingido!'})
    
    if len(justificativa) < 15:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Necessário informar o texto da correção com mínimo 15 caracteres!'})
    
    if len(justificativa) > 1000:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'O texto da correção deve ter até 1000 caracteres!'})
    
    nfe.CCe = True
    nfe.xJust = remove_acentos(justificativa.strip())
    nfe.save()
    nfe.refresh_from_db()

    status, msg_retorno = gera_cce(nfe, empresa)

    if status == 135:
        nfe.CCe = False
        nfe.save()
        nfe.refresh_from_db()

        return JsonResponse({'erro': False, 'status': status, 'mensagem': 'CC-e gerada com sucesso!'})
    else:
        return JsonResponse({'erro': True, 'status': status, 'mensagem': msg_retorno})

@api_view(['POST'])
@csrf_exempt
def cancelar_nfe(request):
    if request.method != 'POST':
        return JsonResponse({'erro': True, 'mensagem': 'Método de requisição inválido!'})

    id_nfe = int(request.POST.get('id'))
    empresa_filial = int(request.POST.get('empresa'))
    justificativa = request.POST.get('justificativa')

    try:
        empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
        nome_tabela = apps.get_model('core', empresa.Tabela)
    except Empresa.DoesNotExist:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Empresa não encontrada!'})

    try:
        nfe = nome_tabela.objects.get(id_nfe=id_nfe)
    except nome_tabela.DoesNotExist:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Nota Fiscal não encontrada!'})
    
    if 'Aut' not in nfe.status_sefaz and 'Carta' not in nfe.status_sefaz:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'NF-e não está como Autorizada!'})
    
    if 'Canc' in nfe.status_sefaz:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'NF-e já foi cancelada!'})

    if len(justificativa) < 20:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Justificativa deve ter no mínimo 20 caracteres!'})

    nfe.Cancelar = True
    nfe.xJust = remove_acentos(justificativa.strip())
    nfe.save()
    nfe.refresh_from_db()
    
    status, msg_retorno = cancela_nfe(nfe, empresa)

    if status == 135:
        nfe.Cancelar = False
        nfe.save()
        nfe.refresh_from_db()

        return JsonResponse({'erro': False, 'status': status, 'mensagem': 'Cancelamento realizado com sucesso!'})
    else:
        return JsonResponse({'erro': True, 'status': status, 'mensagem': msg_retorno})

@api_view(['POST'])
@csrf_exempt
def gerar_gnre(request):
    if request.method != 'POST':
        return JsonResponse({'erro': True, 'mensagem': 'Método de requisição inválido!'})

    id_nfe = int(request.POST.get('id', 0))
    empresa_filial = int(request.POST.get('empresa', 0))
    receita = int(request.POST.get('receita', 0))
    detalhamento_receita = request.POST.get('detalhamento-receita', '')
    data_vencimento = request.POST.get('data-vencimento')
    data_pagamento = request.POST.get('data-pagamento')

    try:
        empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
        nome_tabela = apps.get_model('core', empresa.Tabela)
    except Empresa.DoesNotExist:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Empresa não encontrada!'})

    try:
        nfe = nome_tabela.objects.get(id_nfe=id_nfe)
    except nome_tabela.DoesNotExist:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Nota Fiscal não encontrada!'})
    
    if 'Aut' not in nfe.status_sefaz and 'Carta' not in nfe.status_sefaz:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'NF-e não está como Autorizada!'})
    
    if receita == 100099:
        tipo = 'ST'
    elif receita == 100102:
        tipo = 'DIFAL'
    elif receita == 100129:
        tipo = 'FCP'
    else:
        tipo = ''

    if int(nfe.Pedido) < 100000000:
        gnre_pagamento = GNRE_Pagamentos.objects.using('greenmotor').filter(CodPedido=nfe.Pedido, Tipo=tipo, NFe=nfe.ide_nNF).first()
    else:
        gnre_pagamento = GNRE_Pagamentos.objects.using('lanmax').filter(CodPedido=nfe.Pedido, Tipo=tipo, NFe=nfe.ide_nNF).first()

    if not gnre_pagamento:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': f'Registro não encontrado em GNRE Pagamentos!'})
    
    if gnre_pagamento.Status == 10:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': f'GNRE do pedido {nfe.Pedido} já foi pago!'})
    
    gnre = tem_gnre(nfe.id_nfe, empresa.ide_serie)
    
    if gnre or tem_difal(nfe.id_nfe, empresa.ide_serie):
        if not receita:
            return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Necessário informar receita!'})
        
        rec = GNRE_Receitas.objects.filter(UF=nfe.dest_UF, Codigo=receita)

        if not rec.exists():
            return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'UF Favorecida não atende a receita informada!'})

        dr = GNRE_DetalhamentoReceitas.objects.filter(UF=nfe.dest_UF, Receita=receita)

        if dr.exists():
            if not detalhamento_receita:
                return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Necessário informar o detalhamento da Receita!'})
        else:
            detalhamento_receita = None

        if not data_vencimento:
            return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Necessário informar data de vencimento!'})
        
        if not data_pagamento:
            return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Necessário informar data de pagamento!'})

        gera_xmlgnre(nfe, empresa, detalhamento_receita, data_vencimento, data_pagamento)
        status_envia_gnre = envia_gnre(nfe, empresa, receita)

        if status_envia_gnre == 100:
            if int(nfe.Pedido) < 100000000:
                pedido = Pedido.objects.using('greenmotor').get(cod_pedido=nfe.Pedido)
            else:
                pedido = Pedido.objects.using('lanmax').get(cod_pedido=nfe.Pedido)

            if receita == 100099:
                nro_recibo = pedido.gnre_protocolo
            elif receita == 100102:
                nro_recibo = pedido.difal_protocolo
            elif receita == 100129:
                nro_recibo = pedido.fcp_protocolo
            else:
                nro_recibo = ''

            status_busca_gnre = busca_gnre(nfe, empresa, nro_recibo, receita)

            if status_busca_gnre == 402:
                return JsonResponse({'erro': False, 'status': 100, 'mensagem': 'GNRE gerado com sucesso!'})
            else:
                return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Erro ao buscar GNRE!'})
        else:
            return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'Erro ao gerar GNRE!'})
    else:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'NF-e não possui ST ou DIFAL!'})

@api_view(['POST'])
@csrf_exempt
def enviar_email_nfe(request):
    if request.method != 'POST':
        return JsonResponse({'erro': True, 'mensagem': 'Método de requisição inválido!'})

    empresa_filial = request.POST.get('empresa_filial', 0)
    id_nfe = request.POST.get('id_nfe', 0)
    
    try:
        empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
        nome_tabela = apps.get_model('core', empresa.Tabela)
    except Empresa.DoesNotExist:
        return JsonResponse({'erro': True, 'mensagem': 'Empresa não encontrada!'})

    try:
        nfe = nome_tabela.objects.get(id_nfe=id_nfe)
    except nome_tabela.DoesNotExist:
        return JsonResponse({'erro': True, 'mensagem': 'Nota Fiscal não encontrada!'})
    
    if int(nfe.Pedido) < 100000000 and int(nfe.Pedido) > 0:
        db = 'greenmotor'
    else:
        db = 'lanmax'
    
    if 'Aut' not in nfe.status_sefaz and 'Carta' not in nfe.status_sefaz and nfe.status_sefaz != 'COB faturada':
        return JsonResponse({'erro': True, 'mensagem': 'NF-e não está autorizada!'})
    
    try:
        lista_emails = nfe.dest_eMail.split(';')

        for e in lista_emails:
            info = validate_email(e.strip(), check_deliverability=False)
        # email_cliente = info.normalized
    except EmailNotValidError as e:
        if 'shopee+' in nfe.dest_eMail or nfe.dest_eMail == 'NaoInformado' or nfe.dest_eMail == '@':
            nfe.ECFRef_mod = 0
        else:
            nfe.ECFRef_mod = 3

        nfe.save()
        nfe.refresh_from_db()
        
        return JsonResponse({'erro': True, 'mensagem': str(e)})
    
    pag_ometz = Pagamento.objects.using(db).filter(cod_pedido=nfe.Pedido, conta='Ometz-I', forma='BOL')
    pag_nao_ometz = Pagamento.objects.using(db).filter(cod_pedido=nfe.Pedido, forma='BOL').exclude(conta='Ometz-I')
    pagto = Pagamento.objects.using(db).filter(cod_pedido=nfe.Pedido)

    if controleInterno(int(nfe.Pedido)) and not pagto.exists():
        nfe.ECFRef_mod = 0
        nfe.save()
        nfe.refresh_from_db()

        return JsonResponse({'erro': False, 'mensagem': 'Controle Interno sem forma de pagamento!'})

    if pag_ometz.exists() and not pagto.exists():
        return JsonResponse({'erro': True, 'mensagem': 'Pedido só com boleto Ometz!'})
    
    cursor = connection.cursor()

    if int(nfe.Pedido) < 100000000 and int(nfe.Pedido) > 0:
        cursor.execute('EXEC GreenMotor.dbo.Pedido_Orcamento %s, %s', [nfe.Pedido, 0])
    else:
        cursor.execute('EXEC Lanmax.dbo.Pedido_Orcamento %s, %s', [nfe.Pedido, 0])

    rows = cursor.fetchall()
    rows_ordenados = sorted(rows, key=lambda x: x[4])

    keys = ('cod_pedido', 'func_comissao', 'valor_total', 'observacoes', 'nome_prod', 'descricao', 
            'quantidade', 'valor_unit_ref', 'valor_unit_prom', 'valor_item_ref', 'valor_item_prom', 'aliq_ipi',
            'nome', 'razao_social', 'cnpj', 'inscricao_estadual', 'nome_contato', 'cargo_contato', 'logradouro',
            'numero', 'bairro', 'municipio', 'estado', 'cep', 'telefone', 'telefone2', 'celular', 'email', 
            'mnemonico', 'total_icms_st', 'e_razao_social', 'e_endereco', 'e_cep', 'e_cnpj', 'e_contato', 
            'valor_unit_st', 'total_ipi', 'nacional', 'transportadora', )
    
    orcamentos = [dict(zip(keys, row)) for row in rows_ordenados]

    if int(nfe.Pedido) < 100000000 and int(nfe.Pedido) > 0:
        cursor.execute('SELECT CodPedido, Vencimento, NumParcela, Valor_, Forma, Status, DataDeposito, Obs, Conta FROM GreenMotor.dbo.Pagamentos Where CodPedido = %s ORDER BY Vencimento', [nfe.Pedido, ])
    else:
        cursor.execute('SELECT CodPedido, Vencimento, NumParcela, Valor_, Forma, Status, DataDeposito, Obs, Conta FROM Lanmax.dbo.Pagamentos Where CodPedido = %s ORDER BY Vencimento', [nfe.Pedido, ])
    
    rows = cursor.fetchall()
    keys = ('cod_pedido', 'vencimento', 'num_parcela', 'valor', 'forma', 'status', 'data_deposito', 'obs', 'conta')

    pagamentos = [dict(zip(keys, row)) for row in rows]

    caminho_pdf = gerar_pdf_orcamento(request, orcamentos, pagamentos, nfe.Pedido)
    caminho_anexo = '\\\\192.168.10.235\\Database\\Anexos\\'

    if Path(caminho_pdf).exists():
        arquivo_pedido = 'pedido_' + nfe.Pedido + '.pdf'
        xml_autorizado = nfe.ide_nNF + '-procNFe.xml'
        danfe = nfe.ide_nNF + '-danfe.pdf'
        boleto = 'boletos_' + nfe.ide_nNF + '.pdf'
        dest_CNPJ = nfe.dest_CNPJ if nfe.dest_CNPJ else ''
        dest_CPF = nfe.dest_CPF if nfe.dest_CPF else ''

        if controleInterno(int(nfe.Pedido)):
            anexos = caminho_anexo + arquivo_pedido
        else:
            anexos = caminho_anexo + arquivo_pedido + ';' + caminho_anexo + xml_autorizado + ';' + caminho_anexo + danfe

        if dest_CNPJ == '':
            senha = dest_CPF[:5]
        elif dest_CPF == '':
            senha = dest_CNPJ[:5]
        else:
            senha = ''

        senha_mestre = 'L@nM@x*$30'

        if not controleInterno(int(nfe.Pedido)):
            if Path(get_path_repo(nfe, empresa) + danfe).exists():
                if temBol(nfe, empresa):
                    proteger_pdf(get_path_repo(nfe, empresa) + danfe, caminho_anexo + danfe, senha, senha_mestre)
                else:
                    shutil.copy(get_path_repo(nfe, empresa) + danfe, caminho_anexo + danfe)

        if temBol(nfe, empresa):
            proteger_pdf(caminho_pdf, caminho_anexo + arquivo_pedido, senha, senha_mestre)
        else:
            shutil.copy(caminho_pdf, caminho_anexo + arquivo_pedido)

        if not controleInterno(int(nfe.Pedido)):
            if Path(get_path_repo(nfe, empresa) + xml_autorizado).exists() and not controleInterno(int(nfe.Pedido)):
                shutil.copy(get_path_repo(nfe, empresa) + xml_autorizado, caminho_anexo + xml_autorizado)

        Path(caminho_pdf).unlink(missing_ok=True)

        envimsmBol = empresa.envimsmBol.replace('#destinatario#', nfe.dest_xNome.strip())

        if controleInterno(int(nfe.Pedido)):
            cnpj_formatado = f'{empresa.emit_CNPJ[:2]}.{empresa.emit_CNPJ[2:5]}.{empresa.emit_CNPJ[5:8]}/{empresa.emit_CNPJ[8:12]}-{empresa.emit_CNPJ[12:]}'
            envimsm = empresa.envimsmCob.replace('#pedido#', nfe.Pedido).replace('#emitente#', empresa.emit_xNome).replace('#CNPJ#', cnpj_formatado)
        else:
            envimsm = empresa.envimsm.replace('#emitente#', empresa.emit_xNome).replace('#nNFE#', nfe.ide_nNF).replace('#situacao#', nfe.status_sefaz)

        if (controleInterno(int(nfe.Pedido)) and Path(caminho_anexo + arquivo_pedido).exists()) or (not controleInterno(int(nfe.Pedido)) and Path(caminho_anexo + arquivo_pedido).exists() and Path(caminho_anexo + xml_autorizado).exists() and Path(caminho_anexo + danfe).exists()):
            if temBol(nfe, empresa):
                cc = 'renan@lanmax.com.br,financeiro.lanmax@lanmax.com.br,cobranca@lanmax.com.br'
                # cc = ''
                corpo_email = envimsmBol + '\n\n' + envimsm

                pasta_boletos = Diretorio.objects.filter(CNPJ=empresa.emit_CNPJ, TipoArquivo='cob').first()
                nome_boleto = os.path.join(pasta_boletos.Diretorio, f'boleto_{nfe.ide_nNF}.pdf')

                cursor = connection.cursor()

                if int(nfe.Pedido) < 100000000 and int(nfe.Pedido) > 0:
                    cursor.execute('SELECT * FROM GreenMotor.dbo.boletos WHERE CodPedido = %s AND Conta NOT LIKE %s ORDER BY NossoNum', [nfe.Pedido, 'Ometz%',])
                else:
                    cursor.execute('SELECT * FROM Lanmax.dbo.boletos WHERE CodPedido = %s AND Conta NOT LIKE %s ORDER BY NossoNum', [nfe.Pedido, 'Ometz%',])

                rows = cursor.fetchall()
                keys = (
                    'beneficiario', 'cnpj_benef', 'cod_pedido', 'razao_social', 'endereco', 'cid_est', 'cep', 'cnpj', 'vencimento', 'valor', 'conta', 'ag', 'cc', 'digito', 'carteira',
                    'nosso_num', 'data_pedido', 'num_doc', 'agencia_conta', 'controle_interno', 'gerar_qrcode', 'endereco2', 'bairro', 'cidade', 'estado', 'num_parcela', 'id_location'
                )
                boletos = []

                for row in rows:
                    boletos.append(dict(zip(keys, row)))

                c = canvas.Canvas(nome_boleto, pagesize=A4)
                c.setTitle(f'Boleto {nfe.ide_nNF}')

                # path_bolecode = Constante.objects.using('lanmax').get(CodConst=207)

                for bol in boletos:
                    # QRCode Bolecode
                    #  qrcode_bolecode = f'{path_bolecode.Constante}bolecode_{boleto['cod_pedido']}_{boleto['nosso_num']}.jpg'
                    # status_bolecode = 0

                    # if not Path(qrcode_bolecode).exists():
                    #     status_bolecode = gerar_bolecode(boleto['cod_pedido'], boleto['nosso_num'])

                    #     if status_bolecode != 200:
                    #         return JsonResponse({'erro': True, 'arquivo': None, 'mensagem': 'Ocorreu um erro ao gerar QRCode PIX!'})

                    desenhar_parcela_boleto(c, bol)
                    c.showPage()

                c.save()

                if Path(nome_boleto).exists():
                    proteger_pdf(nome_boleto, caminho_anexo + boleto, senha, senha_mestre)
                    Path(nome_boleto).unlink(missing_ok=True)

                anexos += ';' + caminho_anexo + boleto

                if not Path(caminho_anexo + boleto).exists():
                    return JsonResponse({'erro': True, 'mensagem': 'PDF Boleto não encontrado!'})
            else:
                cc = 'renan@lanmax.com.br'
                corpo_email = envimsm

            if int(nfe.Pedido) < 100000000 and int(nfe.Pedido) > 0:
                novo_email = EmailsAEnviar.objects.using(db).get_or_create(
                    # email_to='renan@lanmax.com.br',
                    email_to=nfe.dest_eMail.replace(';', ','),
                    email_cc=cc,
                    assunto='Pedido n° ' + nfe.Pedido if controleInterno(int(nfe.Pedido)) else 'Emissão de NFe n° ' + str(int(nfe.ide_nNF)),
                    email_body=corpo_email,
                    body_format='plain',
                    attachments=anexos,
                    data=datetime.now(),
                    status=False
                )
            else:
                novo_email = EmailsAEnviar.objects.using(db).get_or_create(
                    email_to=nfe.dest_eMail.replace(';', ','),
                    # email_to='renan@lanmax.com.br',
                    email_cc=cc,
                    assunto='Pedido n° ' + nfe.Pedido if controleInterno(int(nfe.Pedido)) else 'Emissão de NFe n° ' + str(int(nfe.ide_nNF)),
                    email_body=corpo_email,
                    body_format='plain',
                    attachments=anexos,
                    data=datetime.now(),
                    status=False
                )

            nfe.ECFRef_mod = 0
            nfe.save()
            nfe.refresh_from_db()

            return JsonResponse({'erro': False, 'mensagem': 'E-mail criado com sucesso!'})
        else:
            return JsonResponse({'erro': True, 'mensagem': 'Anexos não encontrado!'})
    else:
        return JsonResponse({'erro': True, 'mensagem': 'Ocorreu um erro ao gerar o Orçamento PDF!'})

def gerar_cupom(request, empresa_filial, id_nfe):
    try:
        empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
        nome_tabela = apps.get_model('core', empresa.Tabela)
        nome_tabela_itens = apps.get_model('core', empresa.TabelaItens)
    except Empresa.DoesNotExist:
        return JsonResponse({'erro': True, 'mensagem': 'Empresa não encontrada!'})

    try:
        nfe = nome_tabela.objects.get(id_nfe=id_nfe)
        nfe_itens = nome_tabela_itens.objects.filter(id_nfe=id_nfe).order_by('id_item')
    except nome_tabela.DoesNotExist:
        return JsonResponse({'erro': True, 'mensagem': 'Nota Fiscal não encontrada!'})
    
    # pasta_cupons = os.path.join(settings.BASE_DIR, 'static', 'relatorios')
    # nome_cupom = get_path_repo(nfe, empresa) + f'cupom_{nfe.ide_nNF}.pdf'
    
    # if Path(nome_cupom).is_file():
        # impressora = ''

        # win32api.ShellExecute(
        #     0,
        #     'printto',
        #     nome_cupom,
        #     f'"{impressora}"',
        #     '.',
        #     0
        # )

        # return JsonResponse({'erro': False, 'status': 0, 'mensagem': 'Impressora'})

    cursor = connection.cursor()

    cursor.execute('SELECT fp.Descricao,f.pagamento_vPag FROM FormasPagto_NFE f INNER JOIN FormasPagto fp ON f.pagamento_tPag = fp.Codigo WHERE id_nfe = %s AND ide_serie = %s ORDER BY f.pagamento_nForma', [nfe.id_nfe, nfe.ide_serie,])

    rows = cursor.fetchall()

    keys = ('descricao', 'valor')
    formas_pagto = []

    for row in rows:
        formas_pagto.append(dict(zip(keys, row)))
    
    if nfe.ide_mod != 65:
        return JsonResponse({'erro': True, 'mensagem': 'Não é cupom!'})
    
    pasta_cupons = os.path.join(settings.BASE_DIR, 'static', 'relatorios')
    nome_cupom = os.path.join(pasta_cupons, f'cupom_{nfe.ide_nNF}.pdf')

    desenhar_cupom(empresa, nfe, nfe_itens, formas_pagto)

    # pasta_boletos = os.path.join(settings.BASE_DIR, 'static', 'boletos')
    # nome_boleto = os.path.join(pasta_boletos, f'boleto_{nfe.ide_nNF}.pdf')

    # shutil.copy(nome_arquivo, nome_boleto)

    with open(nome_cupom, "rb") as f:
        buffer = BytesIO(f.read())

    # return JsonResponse({'erro': False, 'arquivo': nome_arquivo, 'mensagem': 'Boleto gerado com sucesso!'})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{nome_cupom}"'
    response.write(buffer.getvalue())
    return response

def retransmitir(request, empresa_filial, id_nfe):
    try:
        empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
        nome_tabela = apps.get_model('core', empresa.Tabela)
    except Empresa.DoesNotExist:
        return JsonResponse({'erro': True, 'mensagem': 'Empresa não encontrada!'})

    try:
        nfe = nome_tabela.objects.get(id_nfe=id_nfe)
    except nome_tabela.DoesNotExist:
        return JsonResponse({'erro': True, 'mensagem': 'Nota Fiscal não encontrada!'})
    
    if 'Aut' in nfe.status_sefaz or 'Carta' in nfe.status_sefaz or 'Canc' in nfe.status_sefaz:
        return JsonResponse({'erro': True, 'status': 0, 'mensagem': 'NF-e/NFC-e já foi emitida!'})
    
    nfe.Transmitir = False
    nfe.XML_Transmitido = False
    nfe.status_sefaz = 'NFe não enviada'
    nfe.save()
    nfe.refresh_from_db()

    return JsonResponse({'erro': False, 'status': 100, 'titulo': 'Retransmitir', 'mensagem': f'NF-e/NFC-e {nfe.ide_nNF} da empresa {empresa.Mnemonico} será retransmitida!'})