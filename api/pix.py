from django.db import connection
from lanmax.models import *
from PIL import Image
import requests, json, base64, io, uuid

def renovar_credencial_itau(empresa_filial):
    url = 'https://sts.itau.com.br/seguranca/v1/certificado/solicitacao'

    conta_lanmax = Conta.objects.using('lanmax').filter(Empresa=empresa_filial).first()

    headers = {
        'content-type': 'text/plain',
        'authorization': 'Bearer ' + conta_lanmax.token_temporario
    }

    with open(conta_lanmax.caminho_arquivo_crt.replace('crt', 'csr'), 'r', encoding='utf-8') as f:
        conteudo_csr = f.read()

    r = requests.post(url, data=conteudo_csr, headers=headers)

    if r.status_cod == 200:
        with open(conta_lanmax.caminho_arquivo_crt, 'w', encoding='utf-8') as f:
            f.write(r.text)
        
        return True

    return False

def get_token_itau(empresa_filial):
    url = "https://sts.itau.com.br/api/oauth/token"

    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'x-itau-flowID': '1',
        'x-itau-correlationID': '2'
    }

    conta_lanmax = Conta.objects.using('lanmax').filter(Empresa=empresa_filial).first()
    form = 'grant_type=client_credentials&client_id='+conta_lanmax.client_id+'&client_secret='+conta_lanmax.client_secret
    
    r = requests.post(url, data=form, headers=headers, cert=(conta_lanmax.caminho_arquivo_crt, conta_lanmax.caminho_arquivo_key))
    token_details = json.loads(r.text)

    if r.status_code == 200:
        return token_details['access_token']
    
    return None

# def gerar_bolecode(cod_pedido, nosso_numero):
#     url = "https://secure.api.itau/pix_recebimentos_conciliacoes/v2/boletos_pix"
#     cursor = connection.cursor()

#     if cod_pedido < 100000000:
#         db = 'greenmotor'
#         cursor.execute('SELECT * FROM GreenMotor.dbo.boletos WHERE CodPedido = %s AND NossoNum = %s', [cod_pedido,nosso_numero,])
#     else:
#         db = 'lanmax'
#         cursor.execute('SELECT * FROM Lanmax.dbo.boletos WHERE CodPedido = %s AND NossoNum = %s', [cod_pedido,nosso_numero,])

#     result = cursor.fetchone()

#     if result:
#         keys = (
#             'beneficiario', 'cnpj_benef', 'cod_pedido', 'razao_social', 'endereco', 'cid_est', 'cep', 'cnpj', 'vencimento', 'valor', 'conta', 'ag', 'cc', 'digito', 'carteira',
#             'nosso_num', 'data_pedido', 'num_doc', 'agencia_conta', 'controle_interno', 'gerar_qrcode', 'endereco2', 'bairro', 'cidade', 'estado', 'num_parcela', 'id_location'
#         )

#         boleto = dict(zip(keys, result))

#         pedido = Pedido.objects.using(db).get(cod_pedido=cod_pedido)
#         conta_lanmax = Conta.objects.using(db).get(Conta=boleto.get('conta'))
#         empresa = Empresa.objects.using('default').get(EmpresaFilial=pedido.empresa_filial.empresa_filial)
#         instr_bol1 = InstrBol.objects.using('default').get(CodInstr=2)
#         instr_bol2 = InstrBol.objects.using('default').get(CodInstr=3)

#         token_itau = get_token_itau(pedido.empresa_filial.empresa_filial)

#         headers = {
#             'x-itau-correlationID': '1',
#             'Content-Type': 'application/json',
#             'Accept': 'application/json',
#             'Authorization': 'Bearer ' + token_itau
#         }

#         id_beneficiario = f'{boleto.get('ag')}{boleto.get('cc').zfill(7)}{boleto.get('digito')}'
#         data_emissao = date.today().strftime('%Y-%m-%d')
#         vencimento = datetime.strptime(boleto.get('vencimento'), '%d/%m/%Y')
#         vencimento_formatado = vencimento.strftime('%Y-%m-%d')
#         valor_titulo = str(boleto.get('valor')).replace('.', '').zfill(18)
#         cgc_pagador = boleto.get('cnpj').replace('.', '').replace('/', '').replace('-', '')

#         if len(cgc_pagador) == 11:
#             tipo_pessoa = 'F'
#         elif len(cgc_pagador) == 14:
#             tipo_pessoa = 'J'

#         data = '{' \
#             '"etapa_processo_boleto": "efetivacao",' \
#             '"beneficiario": {' \
#                 '"id_beneficiario": "'+id_beneficiario+'"' \
#             '},' \
#             '"dado_boleto": {' \
#                 '"descricao_instrumento_cobranca": "boleto_pix",' \
#                 '"tipo_boleto": "a vista",' \
#                 '"codigo_carteira": "109",' \
#                 '"codigo_especie": "01",' \
#                 '"data_emissao": "'+data_emissao+'",' \
#                 '"pagador": {' \
#                     '"pessoa": {' \
#                         '"nome_pessoa": "'+boleto.get('razao_social')+'",' \
#                         '"tipo_pessoa": {' \
#                             '"codigo_tipo_pessoa": "'+tipo_pessoa+'",' \
#                             '"numero_cadastro_nacional_pessoa_juridica": "'+cgc_pagador+'"' \
#                         '}' \
#                     '},' \
#                     '"endereco": {' \
#                         '"nome_logradouro": "'+boleto.get('endereco')+'",' \
#                         '"nome_bairro": "'+boleto.get('bairro')+'",' \
#                         '"nome_cidade": "'+boleto.get('cidade')+'",' \
#                         '"sigla_UF": "'+boleto.get('estado')+'",' \
#                         '"numero_CEP": "'+boleto.get('cep').replace('-', '')+'"' \
#                     '}' \
#                 '},' \
#                 '"dados_individuais_boleto": [' \
#                     '{' \
#                         '"numero_nosso_numero": "'+str(boleto.get('nosso_num'))+'",' \
#                         '"data_vencimento": "'+vencimento_formatado+'",' \
#                         '"valor_titulo": "'+valor_titulo+'",' \
#                         '"data_limite_pagamento": "'+vencimento_formatado+'",' \
#                         '"texto_seu_numero": "'+str(boleto.get('cod_pedido'))+'"' \
#                     '}' \
#                 '],' \
#                 '"lista_mensagem_cobranca": [' \
#                     '{' \
#                         '"mensagem": "'+instr_bol1.Instrucao+'"' \
#                     '},' \
#                     '{' \
#                         '"mensagem": "'+instr_bol2.Instrucao+'"' \
#                     '}' \
#                 '],' \
#                 '"instrucao_cobranca": [' \
#                     '{' \
#                         '"codigo_instrucao_cobranca": "1",' \
#                         '"quantidade_dias_apos_vencimento": 10,' \
#                         '"dia_util": false' \
#                     '}' \
#                 ']' \
#             '},' \
#             '"dados_qrcode": {' \
#                 '"chave": "'+empresa.emit_CNPJ+'"' \
#             '}' \
#         '}'

#         r = requests.post(url, data=data, headers=headers, cert=(conta_lanmax.caminho_arquivo_crt, conta_lanmax.caminho_arquivo_key))

#         print(boleto.get('cod_pedido'), boleto.get('nosso_num'), r.status_code, r.text)

#         if r.status_code == 200:
#             dir_bolecode = Constante.objects.using(db).get(CodConst=207)
#             arquivo_response = dir_bolecode.Constante + 'response_' + str(boleto.get('cod_pedido')) + '_' + str(boleto.get('nosso_num')) + '.txt'

#             with open(arquivo_response, 'w') as arquivo:
#                 arquivo.write(r.text)
#                 arquivo.close()

#             bolecode_details = json.loads(r.text)

#             imgdata = base64.b64decode(bolecode_details['data']['dados_qrcode']['base64'])
#             filename = dir_bolecode.Constante + 'bolecode_' + str(boleto.get('cod_pedido')) + '_' + str(boleto.get('nosso_num')) + '.jpg'

#             img = Image.open(io.BytesIO(imgdata))
#             new_img = img.resize((300, 300))
#             new_img.save(filename)

#         return r.status_code
#     else:
#         return 0

def consulta_webhook():
    conta_lanmax = Conta.objects.using('lanmax').get(Conta='Infin-I')
    # url = "https://secure.api.itau/pix_recebimentos/v2/cob/39af27ad2d4a46a8bc51c0d6caa2ce4f"
    # url = "https://secure.api.itau/pix_recebimentos/v2/pix/0c27c10e292743c7a981b202f1217059"
    url = "https://secure.api.itau/pix_recebimentos/v2/webhook/33833717000173"
    token_itau = get_token_itau(6100)

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token_itau
    }

    data = '{"webhookUrl": "http://192.168.10.42:8000/webhook"}'

    r = requests.put(url, data=data, headers=headers, cert=(conta_lanmax.caminho_arquivo_crt, conta_lanmax.caminho_arquivo_key))

    print(r.status_code, r.text)

def consulta_pix_by_id():
    conta_lanmax = Conta.objects.using('lanmax').get(Conta='Starte-I')
    # url = "https://secure.api.itau/pix_recebimentos/v2/cob/20253646000209F64A4DA4C29B4B7860E6F"
    url = "https://secure.api.itau/pix_recebimentos/v2/pix/2025369373EB666B8111046F682CC8F94F2"
    token_itau = get_token_itau(1001)

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token_itau
    }

    r = requests.get(url, headers=headers, cert=(conta_lanmax.caminho_arquivo_crt, conta_lanmax.caminho_arquivo_key))

    print(r.status_code, r.text)

    if r.status_code == 200:
        with open("C:\\Users\\rmizukosi\\Desktop\\pix_consulta.txt", 'w', encoding='utf-8') as f:
            f.write(r.text)

def consulta_pix(conta):
    conta_lanmax = Conta.objects.using('lanmax').get(Conta=conta)
    # empresa = EmpresaFilial.objects.using('lanmax').get(empresa_filial=conta_lanmax.Empresa)
    # id_conta = f'60701190{str(conta_lanmax.Ag).zfill(4)}{str(conta_lanmax.CC).zfill(13)}'
    url = "https://secure.api.itau/pix_recebimentos/v2/pix?inicio=2025-08-25T00:00:00Z&fim=2025-08-31T23:59:59Z"
    # url = "https://secure.api.itau/pix_recebimentos/v2/cobv?inicio=2025-08-25T07:00:00Z&fim=2025-08-25T23:59:59Z"
    # url = "https://secure.api.itau/pix_recebimentos_conciliacoes/v2/lancamentos_pix?id_conta="+id_conta+"&chaves="+empresa.cnpj+"&data_criacao_lancamento=2025-08-25T07:00,2025-08-25T23:59"
    token_itau = get_token_itau(conta_lanmax.Empresa)
    
    headers = {
        'x-itau-correlationID': 'bc4d8712-904a-47af-a3a0-63751ddb7e56',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token_itau
    }

    r = requests.get(url, headers=headers, cert=(conta_lanmax.caminho_arquivo_crt, conta_lanmax.caminho_arquivo_key))

    # pix_json = json.loads(r.text)

    # for pix in pix_json['pix']:
    #     print(pix.get('valor'))

    # print(r.status_code, r.text)

    if r.status_code == 200:
        with open("C:\\Users\\rmizukosi\\Desktop\\pix_consulta_"+conta+".txt", 'w', encoding='utf-8') as f:
            f.write(r.text)

def gerar_chave_pix(cod_pedido, num_parcela):
    cursor = connection.cursor()

    if cod_pedido <= 9999999:
        cursor.execute(
            "SELECT c.RazaoSocial, c.CNPJ, pa.Vencimento, pa.Valor_, ef.ContaCobranca, ef.CNPJ FROM GreenMotor.dbo.Pagamentos pa INNER JOIN GreenMotor.dbo.Pedidos p ON pa.CodPedido = p.CodPedido " \
            "INNER JOIN GreenMotor.dbo.Clientes c ON p.CodCliente = c.CodCliente INNER JOIN GreenMotor.dbo.EmpresaFilial ef ON p.EmpresaFilial = ef.EmpresaFilial " \
            "WHERE (StatusPed LIKE %s OR StatusPed LIKE %s) AND pa.CodPedido = %s AND NumParcela = %s AND Forma = %s AND Status IS NULL",
            ['Aprov%', 'Conf%', cod_pedido, num_parcela, 'Pix',]
        )
    else:
        cursor.execute(
            "SELECT c.RazaoSocial, c.CNPJ, pa.Vencimento, pa.Valor_, ef.ContaCobranca, ef.CNPJ FROM Lanmax.dbo.Pagamentos pa INNER JOIN Lanmax.dbo.Pedidos p ON pa.CodPedido = p.CodPedido " \
            "INNER JOIN Lanmax.dbo.Clientes c ON p.CodCliente = c.CodCliente INNER JOIN Lanmax.dbo.EmpresaFilial ef ON p.EmpresaFilial = ef.EmpresaFilial " \
            "WHERE (StatusPed LIKE %s OR StatusPed LIKE %s) AND pa.CodPedido = %s AND NumParcela = %s AND Forma = %s AND Status IS NULL",
            ['Aprov%', 'Conf%', cod_pedido, num_parcela, 'Pix',]
        )

    result = cursor.fetchone()

    if result:
        keys = ('razao_social', 'cnpj', 'vencimento', 'valor', 'conta', 'cnpj_empresa')
        titulo_pix = dict(zip(keys, result))

        txid = f'{str(cod_pedido)}{uuid.uuid4().hex[:26].upper()}'
        conta_lanmax = Conta.objects.using('lanmax').get(Conta=titulo_pix.get('conta'))
        url = "https://secure.api.itau/pix_recebimentos/v2/cobv/" + txid
        token_itau = get_token_itau(conta_lanmax.Empresa)

        vencimento_formatado = titulo_pix.get('vencimento').strftime('%Y-%m-%d')
        cnpj_devedor = str(titulo_pix.get('cnpj')).zfill(14) if len(str(titulo_pix.get('cnpj'))) > 11 else str(titulo_pix.get('cnpj')).zfill(11)

        headers = {
            'x-itau-apikey': '96decebf-5c47-4410-95bf-0c4b803e4bb2',
            'x-itau-correlationID': 'bc4d8712-904a-47af-a3a0-63751ddb7e56',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + token_itau
        }

        data = '{' \
            '"calendario": {' \
                '"dataDeVencimento": "'+vencimento_formatado+'"' + \
            '},' \
            '"devedor": {' \
                '"cnpj": "'+cnpj_devedor+'",' \
                '"nome": "'+titulo_pix.get('razao_social')+'"' \
            '},' \
            '"valor": {' \
                '"original": "'+str(titulo_pix.get('valor'))+'"' \
            '},' \
            '"chave": "'+titulo_pix.get('cnpj_empresa')+'"' \
        '}'

        r = requests.put(url, data=data, headers=headers, cert=(conta_lanmax.caminho_arquivo_crt, conta_lanmax.caminho_arquivo_key))

        print(r.status_code, r.text)

        if r.status_code == 201:
            with open("C:\\Users\\rmizukosi\\Desktop\\pix.txt", 'w', encoding='utf-8') as f:
                f.write(r.text)

def cancelar_chave_pix():
    conta_lanmax = Conta.objects.using('lanmax').get(Conta='Lib-I')
    url = "https://secure.api.itau/pix_recebimentos/v2/cob/202611557AB5B0369231941D2B3312FF36B"
    token_itau = get_token_itau(2800)

    print(url)

    headers = {
        'x-itau-apikey': '96decebf-5c47-4410-95bf-0c4b803e4bb2',
        'x-itau-correlationID': 'bc4d8712-904a-47af-a3a0-63751ddb7e56',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token_itau
    }

    data = '{"status": "REMOVIDA_PELO_USUARIO_RECEBEDOR"}'

    r = requests.patch(url, data=data, headers=headers, cert=(conta_lanmax.caminho_arquivo_crt, conta_lanmax.caminho_arquivo_key))

    print(r.status_code, r.text)

    if r.status_code == 200:
        cursor = connection.cursor()
        cursor.execute("UPDATE Lanmax.dbo.Pagamentos SET txid = NULL, pixCopiaECola = NULL WHERE CodPedido = %s", [202611557,])
        
        with open("C:\\Users\\rmizukosi\\Desktop\\pix_cancelado.txt", 'w', encoding='utf-8') as f:
            f.write(r.text)