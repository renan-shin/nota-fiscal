from django.apps import apps
from datetime import datetime

def fncCalculoDV10(numero: str):
    fator = 2
    total = 0

    for digito in reversed(numero):
        parcial = int(digito) * fator

        if parcial > 9:
            parcial = parcial - 9
        
        total += parcial

        fator = 1 if fator == 2 else 2

    dv = (10 - (total % 10)) % 10

    return dv

def fncMontaCodBarras(banco, moeda, valor, carteira, nosso_num, dv, ag, cc, digito, str_vencimento):
    data_limite_antigo = datetime(1997, 10, 7)
    data_limite_novo = datetime(2025, 2, 22)
    vencimento = datetime.strptime(str_vencimento, '%d/%m/%Y')

    if vencimento >= data_limite_novo:
        diferenca_datas = vencimento - data_limite_novo
        fator = diferenca_datas.days
        fator += 1000
    else:
        diferenca_datas = vencimento - data_limite_antigo
        fator = diferenca_datas.days

    valor_seq = int(valor*100)
    str_valor_seq = str(valor_seq).zfill(10)

    codigo_sequencia = f'{banco}{moeda}{fator}{str_valor_seq}{carteira}{nosso_num}{dv}{ag}{cc}{digito}000'
    dvcb = fncCalculaDVCodBarras(codigo_sequencia)

    return f'{codigo_sequencia[:4]}{dvcb}{codigo_sequencia[-39:]}'

def fncCalculaDVCodBarras(sequencia):
    fator = 2
    total = 0
    #print(sequencia)

    for digito in reversed(sequencia):
        parcial = int(digito)

        if fator > 9:
            fator = 2

        parcial *= fator
        total += parcial
        fator += 1

    resto = total % 11
    resultado = 11 - resto

    if resultado >= 10 or resultado == 0:
        return 1

    return resultado

def fncLinhaDigitavel(seq_cod_barra):
    seq1 = f'{seq_cod_barra[:4]}{seq_cod_barra[19:24]}'
    seq2 = f'{seq_cod_barra[24:34]}'
    seq3 = f'{seq_cod_barra[34:44]}'
    seq4 = f'{seq_cod_barra[5:19]}'
    dvcb = f'{seq_cod_barra[4:5]}'

    dv1 = fncCalculoDV10(seq1)
    dv2 = fncCalculoDV10(seq2)
    dv3 = fncCalculoDV10(seq3)

    seq_dv1 = f'{seq1}{dv1}'
    seq_dv2 = f'{seq2}{dv2}'
    seq_dv3 = f'{seq3}{dv3}'

    seq1 = f'{seq_dv1[:5]}.{seq_dv1[5:10]}'
    seq2 = f'{seq_dv2[:5]}.{seq_dv2[5:11]}'
    seq3 = f'{seq_dv3[:5]}.{seq_dv3[5:11]}'

    return f'{seq1} {seq2} {seq3} {dvcb} {seq4}'