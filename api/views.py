from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.apps import apps
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from core.models import *
from lanmax.models import *
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from .reports import *
from pathlib import Path
from nfe_util_2g.utils import *
from datetime import datetime, date
import shutil, requests, os
from .pix import *

empresas_greenmotor = [-3102, -3101, -2003, -2002, -2001, -1002, -1001, 8001, 8003, 8004, 8005, 8006, 8007]

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

    columns = ['Pedido', 'ide_nNF', 'ide_serie', 'status_sefaz', 'dtp', 'dest_xNome']
    order_column_index = int(request.GET.get("order[0][column]", 0))
    order_column = columns[order_column_index]
    order_dir = request.GET.get("order[0][dir]", "asc")

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

    if not xml_autorizado.is_file():
        return JsonResponse({'erro': True, 'mensagem': 'Arquivo XML Autorizado não encontrado!'})

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
        boletos = []

        for row in rows:
            boletos.append(dict(zip(keys, row)))

    pdf = gerar_pdf_danfe(empresa, nfe, nfe_itens, list(boletos))
    caminho_pdf = Path(pdf)

    if caminho_pdf.is_file():
        diretorio = Diretorio.objects.filter(CNPJ=empresa.emit_CNPJ, TipoArquivo='pdfDANFe').first()
        
        # Copia para a pasta DANFE PDF da empresa correspondente
        if Path(diretorio.Diretorio).is_dir():
            if not Path(diretorio.Diretorio + nfe.ide_nNF + '-danfe.pdf').is_file():
                shutil.copy(caminho_pdf, diretorio.Diretorio)
        else:
            return JsonResponse({'erro': True, 'mensagem': 'Pasta da DANFE não encontrada!'})

        diretorio = Diretorio.objects.filter(CNPJ=empresa.emit_CNPJ, TipoArquivo='contabilidadeAut').first()
        mes_nfe = nfe.dhRecbto[5:7]
        ano_nfe = nfe.dhRecbto[:4]
        caminho_nfe = diretorio.Diretorio + ano_nfe + '\\' + mes_nfe + '\\' + nfe.ide_nNF

        # Copia para a pasta REPOSITORIO da empresa correspondente
        if Path(caminho_nfe).is_dir():
            if not Path(caminho_nfe + nfe.ide_nNF + '-danfe.pdf').is_file():
                shutil.copy(caminho_pdf, caminho_nfe)
        else:
            return JsonResponse({'erro': True, 'mensagem': 'Pasta da NF-e não encontrada!'})

        caminho_pdf.unlink()
        return JsonResponse({'erro': False, 'mensagem': f'DANFE gerada com sucesso!'})
    else:
        return JsonResponse({'erro': True, 'mensagem': 'Erro ao gerar a DANFE!'})

    # response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = f'inline; filename="danfe_{nfe.ide_nNF}.pdf"'
    # response.write(pdf)
    # return response

def gerar_boleto(request, cod_pedido):
    cursor = connection.cursor()

    if cod_pedido < 100000000:
        cursor.execute("SELECT Vencimento, Valor_ FROM GreenMotor.dbo.boletos WHERE CodPedido = %s ORDER BY NossoNum", [cod_pedido,])
    else:
        cursor.execute("SELECT * FROM Lanmax.dbo.boletos WHERE CodPedido = %s ORDER BY NossoNum", [cod_pedido,])

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

    nome_arquivo = f'static/relatorios/boletos_{cod_pedido}_{datetime.now().strftime('%d%m%Y_%H%M%S')}.pdf'
    c = canvas.Canvas(nome_arquivo, pagesize=A4)

    # path_bolecode = Constante.objects.using('lanmax').get(CodConst=207)

    for boleto in boletos:
        # QRCode Bolecode
        #  qrcode_bolecode = f'{path_bolecode.Constante}bolecode_{boleto['cod_pedido']}_{boleto['nosso_num']}.jpg'
        # status_bolecode = 0

        # if not Path(qrcode_bolecode).is_file():
        #     status_bolecode = gerar_bolecode(boleto['cod_pedido'], boleto['nosso_num'])

        #     if status_bolecode != 200:
        #         return JsonResponse({'erro': True, 'arquivo': None, 'mensagem': 'Ocorreu um erro ao gerar QRCode PIX!'})

        desenhar_parcela_boleto(c, boleto)
        c.showPage()

    c.save()

    return JsonResponse({'erro': False, 'arquivo': nome_arquivo, 'mensagem': 'Boleto gerado com sucesso!'})

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
            "SELECT c.RazaoSocial, c.CNPJ, pa.Vencimento, pa.Valor_, ef.ContaCobranca, ef.CNPJ FROM GreenMotor.dbo.Pagamentos pa INNER JOIN GreenMotor.dbo.Pedidos p ON pa.CodPedido = p.CodPedido " \
            "INNER JOIN GreenMotor.dbo.Clientes c ON p.CodCliente = c.CodCliente INNER JOIN GreenMotor.dbo.EmpresaFilial ef ON p.EmpresaFilial = ef.EmpresaFilial " \
            "WHERE (StatusPed = %s OR StatusPed LIKE %s) AND pa.CodPedido = %s AND NumParcela = %s AND Forma = %s AND Status IS NULL",
            ['Inicial', 'Pend%', cod_pedido, num_parcela, 'Pix',]
        )

        txid = f'{str(cod_pedido)}{uuid.uuid4().hex[:28].upper()}'
    else:
        cursor.execute(
            "SELECT c.RazaoSocial, c.CNPJ, pa.Vencimento, pa.Valor_, ef.ContaCobranca, ef.CNPJ FROM Lanmax.dbo.Pagamentos pa INNER JOIN Lanmax.dbo.Pedidos p ON pa.CodPedido = p.CodPedido " \
            "INNER JOIN Lanmax.dbo.Clientes c ON p.CodCliente = c.CodCliente INNER JOIN Lanmax.dbo.EmpresaFilial ef ON p.EmpresaFilial = ef.EmpresaFilial " \
            "WHERE (StatusPed = %s OR StatusPed LIKE %s) AND pa.CodPedido = %s AND NumParcela = %s AND Forma = %s AND Status IS NULL",
            ['Inicial', 'Pend%', cod_pedido, num_parcela, 'Pix',]
        )

        txid = f'{str(cod_pedido)}{uuid.uuid4().hex[:26].upper()}'

    result = cursor.fetchone()

    if not result:
        return JsonResponse({'erro': True, 'mensagem': 'Título PIX não encontrado!'})

    keys = ('razao_social', 'cnpj', 'vencimento', 'valor', 'conta', 'cnpj_empresa')
    titulo_pix = dict(zip(keys, result))

    conta_lanmax = Conta.objects.using('lanmax').get(Conta=titulo_pix.get('conta'))
    empresa_filial = EmpresaFilial.objects.using('lanmax').get(empresa_filial=conta_lanmax.Empresa)
    url = "https://secure.api.itau/pix_recebimentos/v2/cob/" + txid
    token_itau = get_token_itau(conta_lanmax.Empresa)

    if not token_itau:
        return JsonResponse({'erro': True, 'mensagem': 'Token Itaú não foi gerado!'})

    # vencimento_formatado = titulo_pix.get('vencimento').strftime('%Y-%m-%d')
    diferenca = titulo_pix.get('vencimento').date() - date.today()
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

    r = requests.put(url, data=data, headers=headers, cert=(conta_lanmax.caminho_arquivo_crt, conta_lanmax.caminho_arquivo_key))

    print(r.status_code, r.text)

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

        return JsonResponse({'erro': False, 'mensagem': 'PIX gerado com sucesso!'})

    return JsonResponse({'erro': True, 'mensagem': 'Ocorreu um erro ao gerar a chave PIX.'})

@csrf_exempt
def consulta_pix(request, conta):
    conta_lanmax = Conta.objects.using('lanmax').get(Conta=conta)
    empresa = EmpresaFilial.objects.using('lanmax').get(empresa_filial=conta_lanmax.Empresa)
    id_conta = f'60701190{str(conta_lanmax.Ag).zfill(4)}{str(conta_lanmax.CC).zfill(13)}'
    # url = "https://secure.api.itau/pix_recebimentos/v2/pix?inicio=2025-08-28T00:00:00Z&fim=2025-08-31T23:59:59Z"
    # url = "https://secure.api.itau/pix_recebimentos/v2/cobv/202536155CE191A2D2CDB40099085B7EF0D"
    url = "https://secure.api.itau/pix_recebimentos_conciliacoes/v2/lancamentos_pix?id_conta="+id_conta+"&chaves="+empresa.cnpj+"&data_criacao_lancamento=2025-08-29T00:00,2025-08-31T23:59"
    token_itau = get_token_itau(conta_lanmax.Empresa)
    
    headers = {
        'x-itau-correlationID': 'bc4d8712-904a-47af-a3a0-63751ddb7e56',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token_itau
    }

    r = requests.get(url, headers=headers, cert=(conta_lanmax.caminho_arquivo_crt, conta_lanmax.caminho_arquivo_key))

    with open('C:\\Users\\rmizukosi\\Desktop\\consulta.txt', 'w', encoding='utf-8') as f:
        f.write(r.text)

    return JsonResponse({'erro': False, 'mensagem': 'Consulta realizada com sucesso!'})

    if r.status_code == 200:
        pix_json = json.loads(r.text)
        cursor = connection.cursor()

        for pix in pix_json['pix']:
            if pix.get('txid'):
                print(pix.get('txid'), pix.get('valor'))
                # cursor.execute("UPDATE GreenMotor.dbo.Pagamentos SET Status = %s WHERE Forma = %s AND txid = %s AND Valor_ = %s", ['OK', 'PIX', pix.get('txid'), pix.get('valor')])
                # cursor.execute("UPDATE Lanmax.dbo.Pagamentos SET Status = %s WHERE Forma = %s AND txid = %s AND Valor_ = %s", ['OK', 'PIX', pix.get('txid'), pix.get('valor')])

        return JsonResponse({'erro': False, 'mensagem': 'Sucesso!'})

    return JsonResponse({'erro': True, 'mensagem': pix_json['detail']})

@csrf_exempt
def consulta_pix(request, conta):
    conta_lanmax = Conta.objects.using('lanmax').get(Conta=conta)
    empresa = EmpresaFilial.objects.using('lanmax').get(empresa_filial=conta_lanmax.Empresa)
    id_conta = f'60701190{str(conta_lanmax.Ag).zfill(4)}{str(conta_lanmax.CC).zfill(13)}'
    url = "https://secure.api.itau/pix_recebimentos/v2/pix?inicio=2025-09-01T00:00:00Z&fim=2025-09-01T23:59:59Z"
    # url = "https://secure.api.itau/pix_recebimentos/v2/cobv/202536155CE191A2D2CDB40099085B7EF0D"
    # url = "https://secure.api.itau/pix_recebimentos_conciliacoes/v2/lancamentos_pix?id_conta="+id_conta+"&chaves="+empresa.cnpj+"&data_criacao_lancamento=2025-08-29T00:00,2025-08-31T23:59"
    token_itau = get_token_itau(conta_lanmax.Empresa)
    
    headers = {
        'x-itau-correlationID': 'bc4d8712-904a-47af-a3a0-63751ddb7e56',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token_itau
    }

    r = requests.get(url, headers=headers, cert=(conta_lanmax.caminho_arquivo_crt, conta_lanmax.caminho_arquivo_key))

    with open('C:\\Users\\rmizukosi\\Desktop\\consulta.txt', 'w', encoding='utf-8') as f:
        f.write(r.text)

    return JsonResponse({'erro': False, 'mensagem': 'Consulta realizada com sucesso!'})

    if r.status_code == 200:
        pix_json = json.loads(r.text)
        cursor = connection.cursor()

        for pix in pix_json['pix']:
            if pix.get('txid'):
                print(pix.get('txid'), pix.get('valor'))
                # cursor.execute("UPDATE GreenMotor.dbo.Pagamentos SET Status = %s WHERE Forma = %s AND txid = %s AND Valor_ = %s", ['OK', 'PIX', pix.get('txid'), pix.get('valor')])
                # cursor.execute("UPDATE Lanmax.dbo.Pagamentos SET Status = %s WHERE Forma = %s AND txid = %s AND Valor_ = %s", ['OK', 'PIX', pix.get('txid'), pix.get('valor')])

        return JsonResponse({'erro': False, 'mensagem': 'Sucesso!'})

    return JsonResponse({'erro': True, 'mensagem': pix_json['detail']})

@csrf_exempt
def cancelar_pix(request):
    cancelar_chave_pix()
    # consulta_pix_by_id()
    return JsonResponse({'erro': False, 'mensagem': 'Sucesso!'})