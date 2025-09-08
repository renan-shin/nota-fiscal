from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Table, TableStyle, Paragraph, Spacer, NextPageTemplate, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.graphics.barcode import code128
from reportlab.graphics.barcode.common import I2of5
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.renderPDF import draw
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from core.models import *
from lanmax.models import *
from io import BytesIO
from utils.pdf import NumberedCanvas
from .boletos import *
from datetime import datetime
from django.apps import apps
from django.conf import settings
from pathlib import Path
import locale, os

# Define o locale para português Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Registra a fonte Calibri
pdfmetrics.registerFont(TTFont('Calibri', 'C:/Windows/Fonts/calibri.ttf'))
pdfmetrics.registerFont(TTFont('Calibri-Bold', 'C:/Windows/Fonts/calibrib.ttf'))
pdfmetrics.registerFont(TTFont('Verdana', 'C:/Windows/Fonts/verdana.ttf'))
pdfmetrics.registerFont(TTFont('Verdana-Bold', 'C:/Windows/Fonts/verdanab.ttf'))

def gerar_pdf_danfe(empresa, nfe, nfe_itens, boletos):
    data_emissao = datetime.strptime(nfe.dhRecbto[0:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    total_nfe = locale.currency(nfe.TotalICMS_vNF, grouping=True)
    endereco_destinatario = nfe.dest_xLgr + ", " + nfe.dest_nro + " - " + nfe.dest_xBairro + " - " + nfe.dest_xMun + "/" + nfe.dest_UF
    num_nfe = nfe.ide_nNF[0:3]+'.'+nfe.ide_nNF[3:6]+'.'+nfe.ide_nNF[6:9]
    chave_nfe = nfe.chave_acesso[0:4]+' '+nfe.chave_acesso[4:8]+' '+nfe.chave_acesso[8:12]+' '+nfe.chave_acesso[12:16]+' '+nfe.chave_acesso[16:20]+' '+nfe.chave_acesso[20:24]+' '+nfe.chave_acesso[24:28]+' '+nfe.chave_acesso[28:32]+' '+nfe.chave_acesso[32:36]+' '+nfe.chave_acesso[36:40]+' '+nfe.chave_acesso[40:44]
    protocolo_autorizacao = nfe.nProt+' '+datetime.strptime(nfe.dhRecbto[0:19], "%Y-%m-%dT%H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")
    cnpj_empresa = f"{empresa.emit_CNPJ[:2]}.{empresa.emit_CNPJ[2:5]}.{empresa.emit_CNPJ[5:8]}/{empresa.emit_CNPJ[8:12]}-{empresa.emit_CNPJ[12:]}"

    if nfe.dest_CNPJ or nfe.dest_CPF == '':
        cgc_destinatario = f"{nfe.dest_CNPJ[:2]}.{nfe.dest_CNPJ[2:5]}.{nfe.dest_CNPJ[5:8]}/{nfe.dest_CNPJ[8:12]}-{nfe.dest_CNPJ[12:]}"
    elif nfe.dest_CPF or nfe.dest_CNPJ == '':
        cgc_destinatario = f"{nfe.dest_CPF[:3]}.{nfe.dest_CPF[3:6]}.{nfe.dest_CPF[6:9]}-{nfe.dest_CPF[9:]}"

    width, height = A4
    left_margin = 2*mm
    right_margin = 2*mm
    top_margin = 2*mm
    bottom_margin = 2*mm

    styles = getSampleStyleSheet()
    small = ParagraphStyle('small', parent=styles["Normal"], fontSize=7, leading=9)
    centralizado = ParagraphStyle('centralizado', alignment=1, leading=9, fontName='Times-Roman')
    centralizado_2 = ParagraphStyle('centralizado', alignment=1, leading=15, fontName='Times-Roman')
    centralizado_3 = ParagraphStyle('centralizado', alignment=1, leading=12, fontName='Times-Roman')
    centralizado_4 = ParagraphStyle('centralizado', alignment=1, leading=20, fontName='Times-Roman')
    centralizado_5 = ParagraphStyle('centralizado', alignment=1, leading=5, fontName='Times-Roman')
    esquerda = ParagraphStyle('esquerda', alignment=0, leading=9, fontName='Times-Roman')
    esquerda_2 = ParagraphStyle('esquerda', alignment=0, leading=10, fontName='Times-Roman')
    esquerda_3 = ParagraphStyle('esquerda', alignment=0, leading=11, fontName='Times-Roman')
    esquerda_4 = ParagraphStyle('esquerda', alignment=0, leading=0, fontName='Times-Roman')
    direita = ParagraphStyle('direita', alignment=2, leading=11, fontName='Times-Roman')
    
    # if (nfe.TotalICMS_vICMSUFDest_Opc and nfe.TotalICMS_vICMSUFDest_Opc > 0) or (nfe.TotalICMS_vFCPUFDest_Opc and nfe.TotalICMS_vFCPUFDest_Opc > 0):
    #     info_difal = "Valores totais do ICMS interestadual: DIFAL da UF destino: "
    #     info_difal = info_difal + locale.currency(nfe.TotalICMS_vICMSUFDest_Opc, grouping=True)
    #     info_difal = info_difal + ' + FCP ' + locale.currency(nfe.TotalICMS_vFCPUFDest_Opc, grouping=True)
    #     info_difal = info_difal + '<br/>'
    # else:
    #     info_difal = ''

    adfisco = nfe.infAdic_infAdFisco or ''
    infcpl = '<br/>' + nfe.infAdic_infCpl if nfe.infAdic_infCpl else ''
    inftrib = '<br/>' + nfe.infAdic_infTrib if nfe.infAdic_infTrib else ''
    # texto = info_difal + adfisco + infcpl + inftrib
    texto = adfisco + infcpl + inftrib

    paragrafo_info_adc = Paragraph("<b><i><font size='4'>INFORMAÇÕES COMPLEMENTARES</font></i></b><br/><font size='6'>"+texto+"</font>", esquerda)
    width_paragrafo, height_paragrafo = paragrafo_info_adc.wrap(130*mm, 0)

    data_dados_adicionais = [
        [
            paragrafo_info_adc,
            Paragraph("<b><i><font size='4'>RESERVADO AO FISCO</font></i></b>", esquerda),
        ],
    ]
    
    tabela_dados_adicionais = Table(
        data_dados_adicionais,
        colWidths=[135*mm, 71*mm],
        #rowHeights=[height_paragrafo+10,]
    )
    tabela_dados_adicionais.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0)
    ]))

    # tabela_issqn.wrap(doc.width, doc.topMargin)
    tabela_dados_adicionais_w, tabela_dados_adicionais_h = tabela_dados_adicionais.wrap(width, top_margin)

    # ------------------------------------
    # Cabeçalho
    def cabecalho(canvas, doc):
        canvas.saveState()

        total = getattr(canvas, '_saved_page_states', None)
        barcode = code128.Code128(nfe.chave_acesso, barHeight=26, barWidth=0.75)

        if total:
            total_pages = len(total)+1
        else:
            total_pages = 1

        tabela_tpnf_dados = [
            [Paragraph(f"<font size='12'>{nfe.ide_tpNF:.0f}</font>", centralizado_2)],
        ]

        tabela_tpnf = Table(tabela_tpnf_dados, colWidths=[5 * mm,])
        tabela_tpnf.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))

        tabela_nfe_dados = [
            [
                Paragraph("<font size='12'>DANFE</font><br/><font size='7'><b>Documento Auxiliar da NOTA FISCAL ELETRÔNICA</b></font>", centralizado),
                '',
            ],
            [
                Paragraph("<b><font size='6'>0 - ENTRADA<br/>1 - SAÍDA</font></b>", esquerda),
                tabela_tpnf,
            ],
            [
                Paragraph(f"<font size='12'>Nº {num_nfe}<br/>SÉRIE: {nfe.ide_serie:.0f}</font>", centralizado_3),
            ],
        ]

        tabela_nfe = Table(tabela_nfe_dados, colWidths=[23 * mm, 10 * mm])

        tabela_nfe.setStyle(TableStyle([
            ('SPAN', (0, 0), (-1, 0)),
            ('SPAN', (0, 2), (-1, 2)),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (0, 0), 0),
            ('TOPPADDING', (0, 2), (0, 2), 0),
            ('TOPPADDING', (0, 1), (0, 1), 5),
            ('TOPPADDING', (0, 1), (1, 1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('LEFTPADDING', (0, 0), (0, 2), 0),
            ('LEFTPADDING', (0, 1), (0, 1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))

        logradouro_emitente = empresa.emit_xLgr or ''
        numero_emitente = ', ' + empresa.emit_nro
        complemento_emitente = ' - ' + empresa.emit_xCpl if empresa.emit_xCpl else ''

        max_font_size = 9
        endereco_emitente = logradouro_emitente + numero_emitente + complemento_emitente
        tamanho_endereco_emitente = ajustar_paragraph(endereco_emitente, 88*mm, max_font_size)

        data = [
            [
                Paragraph(
                    "<b><i><font size='6'>IDENTIFICAÇÃO DO EMITENTE</font></i><br/>" \
                    f"<font size='12'>{empresa.emit_xNome}</font><br/><br/>" \
                    f"<font size='{str(tamanho_endereco_emitente)}'>{endereco_emitente}</font><br/>" \
                    f"<font size='9'>{empresa.emit_xBairro} - {empresa.emit_xMun}/{empresa.emit_UF}</font><br/>" \
                    f"<font size='9'>CEP: {empresa.emit_CEP[0:5]}-{empresa.emit_CEP[5:]}&nbsp;&nbsp;&nbsp;FONE: " \
                    f"({empresa.emit_fone[0:2]}) {empresa.emit_fone[2:6]}-{empresa.emit_fone[6:]}</font><br/>" \
                    "</b>", centralizado_3),
                tabela_nfe,
                barcode,
            ],
            [
                '','',
                Paragraph(
                    "<i><b><font size='6'>CHAVE DE ACESSO</font></b></i><br/>" \
                    "<font size='9'>"+chave_nfe+"</font>", esquerda_2)
            ],
            [
                '','',
                Paragraph(
                    "<font size='8'><b>Consulta de autenticidade no portal nacional da NF-e<br/>" \
                    "www.nfe.fazenda.gov.br/portal<br/>" \
                    "ou no site da Sefaz Autorizadora</b></font>", centralizado)
            ]
        ]

        tabela_1 = Table(data, colWidths=[89 * mm, 35 * mm, 82 * mm])

        tabela_1.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (1, -1), 'TOP'),
            ('VALIGN', (2, 0), (2, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (0, -1), 0),
            ('RIGHTPADDING', (0, 0), (0, -1), 0),
            ('LEFTPADDING', (1, 0), (1, -1), 3),
            ('RIGHTPADDING', (1, 0), (1, -1), 3),
            ('SPAN', (0, 0), (0, -1)),
            ('SPAN', (1, 0), (1, -1)),
            ('LEFTPADDING', (2, 0), (2, 0), 0),
            ('LEFTPADDING', (2, 2), (2, 2), 0),
            ('RIGHTPADDING', (2, 1), (2, -1), 0),
            ('TOPPADDING', (0, 0), (1, -1), 1),
            ('TOPPADDING', (2, 1), (2, 1), 0),
            ('TOPPADDING', (2, 2), (2, 2), 5),
            ('BOTTOMPADDING', (0, 0), (1, -1), 1),
            ('BOTTOMPADDING', (2, 1), (2, 1), 0),
            ('BOTTOMPADDING', (2, 2), (2, 2), 10),
            ('BOTTOMPADDING', (2, 0), (2, 0), 2),
        ]))

        data_ie = [
            [Paragraph("<b><i><font size='4'>INSCRIÇÃO ESTADUAL</font></i></b>", esquerda_4)],
            [Paragraph(f"<font size='11'>{empresa.emit_IE}</font>", centralizado)],
        ]

        tabela_ie = Table(data_ie)

        tabela_ie.setStyle(TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))

        data_protocolo = [
            [Paragraph("<b><i><font size='4'>PROTOCOLO DE AUTORIZAÇÃO DE USO</font></i></b>", esquerda_4)],
            [Paragraph(f"<font size='11'>{protocolo_autorizacao}</font>", centralizado_5)],
        ]

        tabela_protocolo = Table(data_protocolo)

        tabela_protocolo.setStyle(TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))

        data_cnpj = [
            [Paragraph("<b><i><font size='4'>CNPJ</font></i></b>", esquerda_4)],
            [Paragraph(f"<font size='11'>{cnpj_empresa}</font>", centralizado)],
        ]

        tabela_cnpj = Table(data_cnpj)

        tabela_cnpj.setStyle(TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))

        data = [
            [
                Paragraph(f"<b><i><font size='4'>NATUREZA DA OPERAÇÃO</font></i></b><br/><font size='11'>{nfe.ide_natOp}</font>", esquerda_2),
                '',
                tabela_protocolo,
            ],
            [
                tabela_ie,
                Paragraph("<b><i><font size='4'>INSC.EST.DO SUBST.TRIBUTÁRIO</font></i></b>", esquerda_4),
                tabela_cnpj,
            ],
        ]

        tabela_2 = Table(data, colWidths=[70*mm, 61*mm, 75*mm], rowHeights=[18,18])

        tabela_2.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('SPAN', (0, 0), (1, 0)),
        ]))

        data = [
            [Paragraph("<i><b><font size='6'>DADOS DO PRODUTO/SERVIÇO</font></b></i>", esquerda)],
        ]

        tabela_3 = Table(data, colWidths=[200*mm,], rowHeights=[15,])

        tabela_3.setStyle(TableStyle())

        w_1, h_1 = tabela_1.wrap(doc.width, doc.topMargin)
        w_2, h_2 = tabela_2.wrap(doc.width, doc.topMargin)
        w_3, h_3 = tabela_3.wrap(doc.width, doc.topMargin)

        if canvas.getPageNumber() == 1:
            tabela_1.drawOn(canvas, doc.leftMargin, height-h_1-top_margin-69)
            tabela_2.drawOn(canvas, doc.leftMargin, height-h_1-h_2-top_margin-69)
        else:
            tabela_1.drawOn(canvas, doc.leftMargin, height - h_1 - top_margin)
            tabela_2.drawOn(canvas, doc.leftMargin, height - h_1-h_2-top_margin)
            tabela_3.drawOn(canvas, doc.leftMargin, height - h_1-h_2-h_3-top_margin+3)

        canvas.restoreState()

    # ------------------------------------
    # Dados de Recebimento (apenas na primeira página)
    def recebimento(canvas, doc, titulo):
        canvas.saveState()
        canvas.setTitle(titulo)

        data = [
            [
                Paragraph("<font size='7'>Recebemos de "+empresa.emit_xNome+", os produtos constantes da nota fiscal indicada ao lado: " \
                    "Data de emissão: "+data_emissao+", Valor Total: "+total_nfe+", Destinatário: "+nfe.dest_xNome+" "+endereco_destinatario+"</font>", esquerda),
                '',
                Paragraph("<font size='13'>NF-e<br/>Nº "+num_nfe+"<br/>SÉRIE: "+f"{nfe.ide_serie:.0f}"+"</font>", centralizado_2),
            ],
            [
                Paragraph("<b><i><font size='4'>DATA DE RECEBIMENTO</font></i></b>", esquerda_4),
                Paragraph("<b><i><font size='4'>IDENTIFICAÇÃO E ASSINATURA DO RECEBEDOR</font></i></b>", esquerda_4),
                '',
            ],
        ]
        
        tabela = Table(
            data,
            colWidths=[35 * mm, 138 * mm, 33 * mm],
            rowHeights=[30,27]
        )
        tabela.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('SPAN', (0, 0), (1, 0)),
            ('SPAN', (2, 0), (2, -1)),
            ('VALIGN', (0, 0), (1, -1), 'TOP'),
            ('VALIGN', (2, 0), (2, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, 0), 0),
            ('TOPPADDING', (0, 0), (1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (0, 0), 0),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 15),
        ]))

        w, h = tabela.wrap(doc.width, doc.topMargin)

        if canvas.getPageNumber() == 1:
            tabela.drawOn(canvas, doc.leftMargin, A4[1] - h - top_margin)

            canvas.setDash(8, 3)  # 4 pts traço, 3 pts espaço
            canvas.setLineWidth(0.1)
            canvas.line(left_margin, height-h-top_margin-6, width - right_margin, height-h-top_margin-6)
            canvas.setDash([])  # volta para linha sólida depois

        canvas.restoreState()

    def rodape(canvas, doc):
        canvas.saveState()

        # data_issqn = [
        #     [
        #         Paragraph("<i><font size='5'>INSCRIÇÃO MUNICIPAL</font></i>", esquerda),
        #         Paragraph("<i><font size='5'>VALOR TOTAL DOS SERVIÇOS</font></i>", esquerda),
        #         Paragraph("<i><font size='5'>BASE DE CÁLCULO DOS SERVIÇOS</font></i>", esquerda),
        #         Paragraph("<i><font size='5'>VALOR DO ISSQN</font></i>", esquerda),
        #     ],
        # ]
        
        # tabela_issqn = Table(
        #     data_issqn,
        #     colWidths=[50*mm, 50*mm, 50*mm, 50*mm],
        #     rowHeights=[20,]
        # )
        # tabela_issqn.setStyle(TableStyle([
        #     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        #     ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        #     ('LEFTPADDING', (0, 0), (-1, -1), 3),
        #     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        #     ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        #     ('TOPPADDING', (0, 0), (-1, -1), 0)
        # ]))

        if canvas.getPageNumber() == 1:
            canvas.setFont("Times-BoldItalic", 6)
            # canvas.drawString(15, doc.bottomMargin+height_paragrafo+7*mm, "CÁLCULO DO ISSQN")
            # tabela_issqn.drawOn(canvas, doc.leftMargin, doc.bottomMargin+height_paragrafo-1*mm)
            canvas.drawString(15, tabela_dados_adicionais_h+bottom_margin+1*mm, "DADOS ADICIONAIS")
            tabela_dados_adicionais.drawOn(canvas, left_margin, bottom_margin)

        canvas.restoreState()

    # ------------------------------------
    # Templates

    # Frame para conteúdo (abaixo do cabeçalho)
    frame_primeira_pagina = Frame(
        left_margin,
        tabela_dados_adicionais_h+7,
        width - 2*left_margin,
        height-tabela_dados_adicionais_h-205,
        id='framePrimeira'
    )

    frame_outras_paginas = Frame(
        left_margin,
        bottom_margin,
        width - 2*left_margin,
        height-142,
        id='frameOutras'
    )

    primeira_pagina = PageTemplate(
        id='PrimeiraPagina',
        frames=[frame_primeira_pagina],
        onPage=lambda c, d: (recebimento(c, d, 'DANFE ' + nfe.ide_nNF), cabecalho(c, d)),
        onPageEnd=lambda c, d: (rodape(c, d))
    )

    demais_paginas = PageTemplate(
        id='DemaisPaginas',
        frames=[frame_outras_paginas],
        onPage=cabecalho,
    )

    # Caminho para salvar no static
    pasta_destino = os.path.join(settings.BASE_DIR, 'static', 'relatorios')
    os.makedirs(pasta_destino, exist_ok=True)
    caminho_pdf = os.path.join(pasta_destino, f'{nfe.ide_nNF}-danfe.pdf')

    # Documento
    doc = BaseDocTemplate(
        caminho_pdf,
        pagesize=A4,
        leftMargin=left_margin,
        rightMargin=right_margin,
        topMargin=top_margin,
        bottomMargin=bottom_margin
    )

    doc.addPageTemplates([primeira_pagina, demais_paginas])

    # ------------------------------------
    # Conteúdo

    def ajustar_paragraph(texto, col_width, fonte_base, font_name="Times-Roman"):
        tamanho = fonte_base
        while True:
            largura = pdfmetrics.stringWidth(texto, font_name, tamanho)

            if largura <= col_width or tamanho <= 5:
                break
            tamanho -= 1
            
        return tamanho

    flow = []

    # Adiciona NextPageTemplate logo após o conteúdo da primeira página
    flow.append(NextPageTemplate('DemaisPaginas'))

    flow.append(Paragraph("<b><i><font size='6'>DESTINATÁRIO/REMETENTE</font></i></b>", esquerda))

    texto = nfe.dest_xNome
    max_font_size = 11
    tamanho = ajustar_paragraph(texto, 141*mm, max_font_size)

    dados_destinatario_1 = [
        [
            Paragraph("<b><i><font size='4'>NOME/RAZÃO SOCIAL</font></i></b><br/>" \
                "<font size='"+str(tamanho)+"'>"+texto+"</font>", esquerda_3),
            Paragraph("<b><i><font size='4'>CNPJ/CPF/IdEstrangeiro</font></i></b><br/>" \
                f"<font size='11'>{cgc_destinatario}</font>", esquerda_3),
            Paragraph("<b><i><font size='4'>DATA DE EMISSÃO</font></i></b><br/>" \
                f"<font size='11'>{data_emissao}</font>", esquerda_3),
        ]
    ]

    tabela_destinatario_1 = Table(dados_destinatario_1, colWidths=[147*mm, 35*mm, 24*mm], rowHeights=[18,])
    tabela_destinatario_1.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    if nfe.dest_xCpl:
        texto_endereco = nfe.dest_xLgr + ', ' + nfe.dest_nro + ' - ' + nfe.dest_xCpl
    else:
        texto_endereco = nfe.dest_xLgr + ', ' + nfe.dest_nro

    tamanho_fonte_endereco = ajustar_paragraph(texto_endereco, 111*mm, max_font_size)

    texto_bairro = nfe.dest_xBairro
    tamanho_fonte_bairro = ajustar_paragraph(texto_bairro, 41*mm, max_font_size)

    dados_destinatario_2 = [
        [
            Paragraph("<b><i><font size='4'>ENDEREÇO</font></i></b><br/>" \
                "<font size='"+str(tamanho_fonte_endereco)+"'>"+texto_endereco+"</font>", esquerda_3),
            Paragraph("<b><i><font size='4'>BAIRRO/DISTRITO</font></i></b><br/>" \
                "<font size='"+str(tamanho_fonte_bairro)+"'>"+texto_bairro+"</font>", esquerda_3),
            Paragraph("<b><i><font size='4'>CEP</font></i></b><br/>" \
                f"<font size='11'>{nfe.dest_CEP[:5]}-{nfe.dest_CEP[5:]}</font>", esquerda_3),
            Paragraph("<b><i><font size='4'>DATA DE SAÍDA/ENTRADA</font></i></b><br/>" \
                "<font size='11'></font>", esquerda_3),
        ]
    ]

    tabela_destinatario_2 = Table(dados_destinatario_2, colWidths=[116*mm, 46*mm, 20*mm, 24*mm], rowHeights=[18,])
    tabela_destinatario_2.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    texto_municipio = nfe.dest_xMun
    tamanho_fonte_municipio = ajustar_paragraph(texto_municipio, 86*mm, max_font_size)

    dados_destinatario_3 = [
        [
            Paragraph("<b><i><font size='4'>MUNICÍPIO</font></i></b><br/>" \
                "<font size='"+str(tamanho_fonte_municipio)+"'>"+texto_municipio+"</font>", esquerda_3),
            Paragraph("<b><i><font size='4'>FONE/FAX</font></i></b><br/>" \
                f"<font size='11'>{nfe.dest_fone or ''}</font>", esquerda_3),
            Paragraph("<b><i><font size='4'>UF</font></i></b><br/>" \
                f"<font size='11'>{nfe.dest_UF}</font>", esquerda_3),
            Paragraph("<b><i><font size='4'>INSCRIÇÃO ESTADUAL</font></i></b><br/>" \
                f"<font size='11'>{nfe.dest_IE or ''}</font>", esquerda_3),
            Paragraph("<b><i><font size='4'>HORA DE SAÍDA</font></i></b><br/>" \
                "<font size='11'></font>", esquerda_3),
        ]
    ]

    tabela_destinatario_3 = Table(dados_destinatario_3, colWidths=[92*mm, 40*mm, 10*mm, 40*mm, 24*mm], rowHeights=[18,])
    tabela_destinatario_3.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    flow.append(tabela_destinatario_1)
    flow.append(tabela_destinatario_2)
    flow.append(tabela_destinatario_3)

    if nfe.entrega_xLgr != '':
        texto_razao_entrega = nfe.entrega_xNome or ''
        tamanho_fonte_razao_entrega = ajustar_paragraph(texto_razao_entrega, 120*mm, max_font_size)
        texto_entrega_ie = nfe.entrega_IE or ''

        if nfe.entrega_CNPJ or nfe.entrega_CPF == '':
            cgc_entrega = f"{nfe.entrega_CNPJ[:2]}.{nfe.entrega_CNPJ[2:5]}.{nfe.entrega_CNPJ[5:8]}/{nfe.entrega_CNPJ[8:12]}-{nfe.entrega_CNPJ[12:]}"
        elif nfe.entrega_CPF or nfe.entrega_CNPJ == '':
            cgc_entrega = f"{nfe.entrega_CPF[:3]}.{nfe.entrega_CPF[3:6]}.{nfe.entrega_CPF[6:9]}-{nfe.entrega_CPF[9:]}"

        dados_entrega = [
            [
                Paragraph("<b><i><font size='4'>NOME/RAZÃO SOCIAL</font></i></b><br/>" \
                    "<font size='"+str(tamanho_fonte_razao_entrega)+"'>"+texto_razao_entrega+"</font>", esquerda_3),
                Paragraph("<b><i><font size='4'>CNPJ/CPF</font></i></b><br/>" \
                    "<font size='11'>"+cgc_entrega+"</font>", esquerda_3),
                Paragraph("<b><i><font size='4'>INSCRIÇÃO ESTADUAL</font></i></b><br/>" \
                    "<font size='11'>"+texto_entrega_ie+"</font>", esquerda_3),
            ],
        ]

        tabela_entrega_1 = Table(dados_entrega, colWidths=[134*mm, 36*mm, 36*mm], rowHeights=[18,])
        tabela_entrega_1.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))

        flow.append(Paragraph("<b><i><font size='6'>INFORMAÇÕES DO LOCAL DE ENTREGA</font></i></b>", esquerda))
        flow.append(tabela_entrega_1)

        texto_nro_entrega = ', ' + nfe.entrega_nro if nfe.entrega_nro else ''
        texto_cpl_entrega = ' - ' + nfe.entrega_xCpl if nfe.entrega_xCpl else ''
        texto_endereco_entrega = nfe.entrega_xLgr + texto_nro_entrega + texto_cpl_entrega
        tamanho_fonte_endereco_entrega = ajustar_paragraph(texto_endereco_entrega, 114*mm, max_font_size)
        tamanho_fonte_bairro_entrega = ajustar_paragraph(nfe.entrega_xBairro, 50*mm, max_font_size)

        dados_entrega = [
            [
                Paragraph("<b><i><font size='4'>ENDEREÇO</font></i></b><br/>" \
                    "<font size='"+str(tamanho_fonte_endereco_entrega)+"'>"+texto_endereco_entrega+"</font>", esquerda_3),
                Paragraph("<b><i><font size='4'>BAIRRO/DISTRITO</font></i></b><br/>" \
                    "<font size='"+str(tamanho_fonte_bairro_entrega)+"'>"+nfe.entrega_xBairro+"</font>", esquerda_3),
                Paragraph("<b><i><font size='4'>CEP</font></i></b><br/>" \
                    "<font size='11'>"+nfe.entrega_CEP[:5]+'-'+nfe.entrega_CEP[5:]+"</font>", esquerda_3),
            ]
        ]

        tabela_entrega_2 = Table(dados_entrega, colWidths=[109*mm, 61*mm, 36*mm], rowHeights=[18,])
        tabela_entrega_2.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))

        flow.append(tabela_entrega_2)

        tamanho_fonte_municipio_entrega = ajustar_paragraph(nfe.entrega_xMun, 154*mm, max_font_size)
        texto_fone_entrega = nfe.entrega_fone or ''

        dados_entrega = [
            [
                Paragraph("<b><i><font size='4'>MUNICÍPIO</font></i></b><br/>" \
                    "<font size='"+str(tamanho_fonte_endereco_entrega)+"'>"+nfe.entrega_xMun+"</font>", esquerda_3),
                Paragraph("<b><i><font size='4'>UF</font></i></b><br/>" \
                    "<font size='11'>"+nfe.entrega_UF+"</font>", esquerda_3),
                Paragraph("<b><i><font size='4'>FONE/FAX</font></i></b><br/>" \
                    "<font size='11'>"+texto_fone_entrega+"</font>", esquerda_3),
            ]
        ]

        tabela_entrega_3 = Table(dados_entrega, colWidths=[160*mm, 10*mm, 36*mm], rowHeights=[18,])
        tabela_entrega_3.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))

        flow.append(tabela_entrega_3)

    if len(boletos) > 0:
        num_linhas = 3
        num_colunas = 5
        dados_fatura = []
        index = 0

        for linha in range(num_linhas):
            linha_dados = []
            for coluna in range(num_colunas):
                if index >= 14 and len(boletos) >= 15:
                    linha_dados.append(Paragraph("<font size='6'>Existem mais parcelas. Confira no XML.</font>", esquerda))
                    break
                elif index < len(boletos):
                    item = boletos[index]
                    vencimento = boletos[index]['vencimento'].strftime('%d/%m/%Y')
                    texto_boleto = str(index+1).zfill(3)+'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+vencimento+'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+locale.currency(boletos[index]['valor'], grouping=True)

                    linha_dados.append(Paragraph("<font size='7'>"+texto_boleto+"</font>", esquerda))
                else:
                    linha_dados.append('')

                index += 1
            
            dados_fatura.append(linha_dados)

        tabela_fatura = Table(dados_fatura, colWidths=[41.15*mm, 41.15*mm, 41.15*mm, 41.15*mm], rowHeights=[10,10,10,])
        tabela_fatura.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.black),
            ('LINEBEFORE', (0, 0), (0, -1), 0.5, colors.black),
            ('LINEAFTER', (0, 0), (-1, -1), 0.5, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))

        flow.append(Paragraph("<b><i><font size='6'>FATURA/DUPLICATA</font></i></b>", esquerda))
        flow.append(tabela_fatura)

    flow.append(Paragraph("<b><i><font size='6'>CÁLCULO DO IMPOSTO</font></i></b>", esquerda))

    dados_cabec_imposto = [
        [
            Paragraph("<b><i><font size='4'>BASE DE CÁL. DO ICMS</font></i></b>", esquerda_4),
            Paragraph("<b><i><font size='4'>VALOR DO ICMS</font></i></b>", esquerda_4),
            Paragraph("<b><i><font size='4'>BASE DE CÁLC. ICMS S.T.</font></i></b>", esquerda_4),
            Paragraph("<b><i><font size='4'>VALOR DO ICMS SUBST.</font></i></b>", esquerda_4),
            Paragraph("<b><i><font size='4'>V. IMP. IMPORTAÇÃO</font></i></b>", esquerda_4),
            Paragraph("<b><i><font size='4'>V. ICMS UF REMET.</font></i></b>", esquerda_4),
            Paragraph("<b><i><font size='4'>V. FCP UF DEST.</font></i></b>", esquerda_4),
            Paragraph("<b><i><font size='4'>V. TOTAL PRODUTOS</font></i></b>", esquerda_4),
        ]
    ]

    tabela_cabec_imposto_1 = Table(dados_cabec_imposto, colWidths=[25.7*mm, 25.7*mm, 25.7*mm, 25.7*mm, 25.7*mm, 25.7*mm], rowHeights=[5,])
    tabela_cabec_imposto_1.setStyle(TableStyle([
        ('LINEBEFORE', (0, 0), (-1, -1), 0.5, colors.black),
        ('LINEAFTER', (0, 0), (-1, -1), 0.5, colors.black),
        ('LINEABOVE', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    flow.append(tabela_cabec_imposto_1)

    vbc_formatado = f"{nfe.TotalICMS_vBC or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    vicms_formatado = f"{nfe.TotalICMS_vICMS or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    vbcst_formatado = f"{nfe.TotalICMS_vBCST or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    vst_formatado = f"{nfe.TotalICMS_vST or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    vii_formatado = f"{nfe.TotalICMS_vII or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    vdifalremet_formatado = f"{nfe.TotalICMS_vICMSUFRemet_Opc or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    vfcp_formatado = f"{nfe.TotalICMS_vFCPUFDest_Opc or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    vprod_formatado = f"{nfe.TotalICMS_vProd or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    dados_imposto = [
        [
            Paragraph("<font size='11'>"+vbc_formatado+"</font>", direita),
            Paragraph("<font size='11'>"+vicms_formatado+"</font>", direita),
            Paragraph("<font size='11'>"+vbcst_formatado+"</font>", direita),
            Paragraph("<font size='11'>"+vst_formatado+"</font>", direita),
            Paragraph("<font size='11'>"+vii_formatado+"</font>", direita),
            Paragraph("<font size='11'>"+vdifalremet_formatado+"</font>", direita),
            Paragraph("<font size='11'>"+vfcp_formatado+"</font>", direita),
            Paragraph("<font size='11'>"+vprod_formatado+"</font>", direita),
        ]
    ]

    tabela_imposto_1 = Table(dados_imposto, colWidths=[25.7*mm, 25.7*mm, 25.7*mm, 25.7*mm, 25.7*mm, 25.7*mm], rowHeights=[13,])
    tabela_imposto_1.setStyle(TableStyle([
        ('LINEBEFORE', (0, 0), (-1, -1), 0.5, colors.black),
        ('LINEAFTER', (0, 0), (-1, -1), 0.5, colors.black),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    flow.append(tabela_imposto_1)

    dados_cabec_imposto = [
        [
            Paragraph("<b><i><font size='4'>VALOR DO FRETE</font></i></b>", esquerda_4),
            Paragraph("<b><i><font size='4'>VALOR DO SEGURO</font></i></b>", esquerda_4),
            Paragraph("<b><i><font size='4'>DESCONTO</font></i></b>", esquerda_4),
            Paragraph("<b><i><font size='4'>OUTRAS DESPESAS</font></i></b>", esquerda_4),
            Paragraph("<b><i><font size='4'>VALOR TOTAL IPI</font></i></b>", esquerda_4),
            Paragraph("<b><i><font size='4'>V. ICMS UF DEST.</font></i></b>", esquerda_4),
            Paragraph("<b><i><font size='4'>V. TOT. TRIB.</font></i></b>", esquerda_4),
            Paragraph("<b><i><font size='4'>V. TOTAL DA NOTA</font></i></b>", esquerda_4),
        ]
    ]

    tabela_cabec_imposto_2 = Table(dados_cabec_imposto, colWidths=[25.7*mm, 25.7*mm, 25.7*mm, 25.7*mm, 25.7*mm, 25.7*mm], rowHeights=[5,])
    tabela_cabec_imposto_2.setStyle(TableStyle([
        ('LINEBEFORE', (0, 0), (-1, -1), 0.5, colors.black),
        ('LINEAFTER', (0, 0), (-1, -1), 0.5, colors.black),
        ('LINEABOVE', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    flow.append(tabela_cabec_imposto_2)

    vfrete_formatado = f"{nfe.TotalICMS_vFrete or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    vseg_formatado = f"{nfe.TotalICMS_vSeg or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    vdesc_formatado = f"{nfe.TotalICMS_vDesc or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    voutro_formatado = f"{nfe.TotalICMS_vOutro or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    vipi_formatado = f"{nfe.TotalICMS_vIPI or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    vdifaldest_formatado = f"{nfe.TotalICMS_vICMSUFDest_Opc or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    vtottrib_formatado = f"{nfe.TotalICMS_vTotTrib or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    vnf_formatado = f"{nfe.TotalICMS_vNF or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    dados_imposto = [
        [
            Paragraph("<font size='11'>"+vfrete_formatado+"</font>", direita),
            Paragraph("<font size='11'>"+vseg_formatado+"</font>", direita),
            Paragraph("<font size='11'>"+vdesc_formatado+"</font>", direita),
            Paragraph("<font size='11'>"+voutro_formatado+"</font>", direita),
            Paragraph("<font size='11'>"+vipi_formatado+"</font>", direita),
            Paragraph("<font size='11'>"+vdifaldest_formatado+"</font>", direita),
            Paragraph("<font size='11'>"+vtottrib_formatado+"</font>", direita),
            Paragraph("<font size='11'>"+vnf_formatado+"</font>", direita),
        ]
    ]

    tabela_imposto_2 = Table(dados_imposto, colWidths=[25.7*mm, 25.7*mm, 25.7*mm, 25.7*mm, 25.7*mm, 25.7*mm], rowHeights=[13,])
    tabela_imposto_2.setStyle(TableStyle([
        ('LINEBEFORE', (0, 0), (-1, -1), 0.5, colors.black),
        ('LINEAFTER', (0, 0), (-1, -1), 0.5, colors.black),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    flow.append(tabela_imposto_2)

    flow.append(Paragraph("<b><i><font size='6'>TRANSPORTADOR/VOLUMES TRANSPORTADOS</font></i></b>", esquerda))

    transp_nome = nfe.transporta_xNome or ''
    tamanho_fonte_transp_nome = ajustar_paragraph(transp_nome, 99*mm, max_font_size)

    if (nfe.transporta_CNPJ and nfe.transporta_CNPJ != '') and (not nfe.transporta_CPF or nfe.transporta_CPF == ''):
        cgc_transp = f"{nfe.transporta_CNPJ[:2]}.{nfe.transporta_CNPJ[2:5]}.{nfe.transporta_CNPJ[5:8]}/{nfe.transporta_CNPJ[8:12]}-{nfe.transporta_CNPJ[12:]}"
    elif (nfe.transporta_CPF and nfe.transporta_CPF != '') and (not nfe.transporta_CNPJ or nfe.transporta_CNPJ == ''):
        cgc_transp = f"{nfe.transporta_CPF[:3]}.{nfe.transporta_CPF[3:6]}.{nfe.transporta_CPF[6:9]}-{nfe.transporta_CPF[9:]}"
    else:
        cgc_transp = ''

    if nfe.transp_modFrete == '0':
        modfrete = '0-Rem (CIF)'
    elif nfe.transp_modFrete == '1':
        modfrete = '1-Dest (FOB)'
    else:
        modfrete = '9-Sem transp.'

    dados_transp = [
        [
            Paragraph("<b><i><font size='4'>RAZÃO SOCIAL</font></i></b><br/>" \
                "<font size='"+str(tamanho_fonte_transp_nome)+"'>"+transp_nome+"</font>", esquerda_3),
            Paragraph("<b><i><font size='4'>FRETE POR CONTA</font></i></b><br/>" \
                "<font size='9'>"+modfrete+"</font>", esquerda_3),
            Paragraph("<b><i><font size='4'>CÓDIGO ANTT</font></i></b>", esquerda_3),
            Paragraph("<b><i><font size='4'>PLACA DO VEÍCULO</font></i></b>", esquerda_3),
            Paragraph("<b><i><font size='4'>UF</font></i></b>", esquerda_3),
            Paragraph("<b><i><font size='4'>CNPJ/CPF</font></i></b><br/>" \
                "<font size='11'>"+cgc_transp+"</font>", esquerda_3),
        ]
    ]

    tabela_transp_1 = Table(dados_transp, colWidths=[105*mm, 21*mm, 15*mm, 20*mm, 10*mm, 35*mm], rowHeights=[18,])
    tabela_transp_1.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    flow.append(tabela_transp_1)

    transp_endereco = nfe.transporta_xEnder or ''
    tamanho_fonte_transp_endereco = ajustar_paragraph(transp_endereco, 99*mm, max_font_size)
    transp_municipio = nfe.transporta_xMun or ''
    tamanho_fonte_transp_mun = ajustar_paragraph(transp_municipio, 56*mm, max_font_size)
    transp_uf = nfe.transporta_UF or ''
    transp_ie = nfe.transporta_IE or ''

    dados_transp = [
        [
            Paragraph("<b><i><font size='4'>ENDEREÇO</font></i></b><br/>" \
                "<font size='"+str(tamanho_fonte_transp_endereco)+"'>"+transp_endereco+"</font>", esquerda_3),
            Paragraph("<b><i><font size='4'>MUNICÍPIO</font></i></b><br/>" \
                "<font size='"+str(tamanho_fonte_transp_mun)+"'>"+transp_municipio+"</font>", esquerda_3),
            Paragraph("<b><i><font size='4'>UF</font></i></b><br/>" \
                "<font size='11'>"+transp_uf+"</font>", esquerda_3),
            Paragraph("<b><i><font size='4'>INSCRIÇÃO ESTADUAL</font></i></b><br/>" \
                "<font size='11'>"+transp_ie+"</font>", esquerda_3),
        ]
    ]

    tabela_transp_2 = Table(dados_transp, colWidths=[105*mm, 56*mm, 10*mm, 35*mm], rowHeights=[18,])
    tabela_transp_2.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    flow.append(tabela_transp_2)

    vol_qvol = f"{nfe.vol_qVol:.0f}" if nfe.vol_qVol else ''
    vol_esp = nfe.vol_esp or ''
    vol_marca = nfe.vol_marca or ''
    vol_nvol = nfe.vol_nVol or ''
    vol_pesol = f"{nfe.vol_pesoL or 0:,.3f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    vol_pesob = f"{nfe.vol_pesoB or 0:,.3f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    dados_transp = [
        [
            Paragraph("<b><i><font size='4'>QUANTIDADE</font></i></b><br/>" \
                "<font size='11'>"+str(vol_qvol)+"</font>", esquerda_3),
            Paragraph("<b><i><font size='4'>ESPÉCIE</font></i></b><br/>" \
                "<font size='11'>"+vol_esp+"</font>", esquerda_3),
            Paragraph("<b><i><font size='4'>MARCA</font></i></b><br/>" \
                "<font size='11'>"+vol_marca+"</font>", esquerda_3),
            Paragraph("<b><i><font size='4'>NUMERAÇÃO</font></i></b><br/>" \
                "<font size='11'>"+vol_nvol+"</font>", esquerda_3),
            Paragraph("<b><i><font size='4'>PESO BRUTO</font></i></b><br/>" \
                "<font size='11'>"+vol_pesob+"</font>", esquerda_3),
            Paragraph("<b><i><font size='4'>PESO LÍQUIDO</font></i></b><br/>" \
                "<font size='11'>"+vol_pesol+"</font>", esquerda_3),
        ]
    ]

    tabela_transp_3 = Table(dados_transp, colWidths=[17*mm, 42*mm, 42*mm, 51*mm, 27*mm, 27*mm], rowHeights=[18,])
    tabela_transp_3.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    flow.append(tabela_transp_3)

    flow.append(Paragraph("<b><i><font size='6'>DADOS DO PRODUTO/SERVIÇO</font></i></b>", esquerda))

    dados_itens = [
        [
            Paragraph("<b><font size='4'>CÓDIGO PRODUTO</font></b>", centralizado_5),
            Paragraph("<b><font size='4'>DESCRIÇÃO DO PRODUTO/SERVIÇO</font></b>", centralizado_5),
            Paragraph("<b><font size='4'>NCM/SH</font></b>", centralizado_5),
            Paragraph("<b><font size='4'>CST</font></b>", centralizado_5),
            Paragraph("<b><font size='4'>CFOP</font></b>", centralizado_5),
            Paragraph("<b><font size='4'>UNID.</font></b>", centralizado_5),
            Paragraph("<b><font size='4'>QUANT.</font></b>", centralizado_5),
            Paragraph("<b><font size='4'>VALOR UNITÁRIO</font></b>", centralizado_5),
            Paragraph("<b><font size='4'>VALOR TOTAL</font></b>", centralizado_5),
            Paragraph("<b><font size='4'>BC ICMS</font></b>", centralizado_5),
            Paragraph("<b><font size='4'>VALOR ICMS</font></b>", centralizado_5),
            Paragraph("<b><font size='4'>VALOR IPI</font></b>", centralizado_5),
            Paragraph("<b><font size='4'>ALIQ. ICMS</font></b>", centralizado_5),
            Paragraph("<b><font size='4'>ALIQ. IPI</font></b>", centralizado_5),
        ],
    ]

    for item in nfe_itens:
        valor_unitario = f"{item.prod_vUnCOM or 0:,.3f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        valor_total = f"{item.prod_vProd or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        predbc = f"{item.icms_pRedBC or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        icms_bc = f"{item.icms_vBC or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        valor_icms = f"{item.icms_vICMS or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        valor_ipi = f"{item.IPI_vIPI or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        aliq_icms = f"{item.icms_pICMS or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        aliq_ipi = f"{item.IPI_pIPI or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        cst = f"{item.icms_orig or ''}{item.icms_CST or ''}"
        infAdProd = item.det_infAdprod or ''
        numserie = item.NumSerie or ''
        descricao_prod = item.prod_xProd or ''
        mvast = f"{item.icms_pMVAST or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        bcst = f"{item.icms_vBCST or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        picmsst = f"{item.icms_pICMSST or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        vicmsst = f"{item.icms_vICMSST or 0:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        texto_descricao_prod = descricao_prod
        texto_st = ''
        texto_pRedBC = ''

        if item.icms_pRedBC and item.icms_pRedBC > 0:
            texto_pRedBC = 'pRedBC=' + predbc + '%'

        if texto_pRedBC != '':
            texto_descricao_prod = texto_descricao_prod + '<br/>' + texto_pRedBC

        if item.icms_vICMSST and item.icms_vICMSST > 0:
            texto_st = 'IVA=' + mvast + '% pIcmsSt=' + picmsst + '% BcIcmsSt=' + bcst + ' vIcmsSt=' + vicmsst

        if texto_st != '':
            texto_descricao_prod = texto_descricao_prod + '<br/>' + texto_st

        if infAdProd != '' and numserie != '':
            texto_infAdProd = infAdProd + '|' + numserie
        else:
            texto_infAdProd = infAdProd + numserie

        if texto_infAdProd != '':
            texto_descricao_prod = texto_descricao_prod + "<br/>" + texto_infAdProd

        dados_itens.append(
            [
                Paragraph(f"<font size='7'>{item.prod_cProd or ''}</font>", esquerda),
                Paragraph(f"<font size='7'>{texto_descricao_prod}</font>", esquerda),
                Paragraph(f"<font size='7'>{item.prod_NCM or ''}</font>", centralizado),
                Paragraph(f"<font size='7'>{cst}</font>", centralizado),
                Paragraph(f"<font size='7'>{item.prod_CFOP or '':.0f}</font>", centralizado),
                Paragraph(f"<font size='7'>{item.prod_uCOM or ''}</font>", centralizado),
                Paragraph(f"<font size='7'>{item.prod_qCOM or '':.0f}</font>", direita),
                Paragraph(f"<font size='7'>{valor_unitario}</font>", direita),
                Paragraph(f"<font size='7'>{valor_total}</font>", direita),
                Paragraph(f"<font size='7'>{icms_bc}</font>", direita),
                Paragraph(f"<font size='7'>{valor_icms}</font>", direita),
                Paragraph(f"<font size='7'>{valor_ipi}</font>", direita),
                Paragraph(f"<font size='7'>{aliq_icms}</font>", centralizado),
                Paragraph(f"<font size='7'>{aliq_ipi}</font>", centralizado),
            ]
        )

    tabela_itens = Table(dados_itens, colWidths=[21*mm, 52.5*mm, 12*mm, 7.2*mm, 7.2*mm, 7*mm, 9.7*mm, 15.5*mm, 15.5*mm, 15.5*mm, 13.5*mm, 13.5*mm, 8*mm, 8*mm], repeatRows=1)
    tabela_itens.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
        ('LINEBELOW', (0, 1), (-1, -2), 0.5, colors.black, None, [1, 2]),
        ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.black),
        ('LINEBEFORE', (0, 0), (-1, -1), 0.5, colors.black),
        ('LINEAFTER', (-1, 0), (-1, -1), 0.5, colors.black),
        #('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, 0), 1),
        ('TOPPADDING', (0, 1), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 1),
    ]))

    flow.append(tabela_itens)

    doc.build(flow, canvasmaker=NumberedCanvas)
    return caminho_pdf

    # pdf = buffer.getvalue()
    # buffer.close()
    # return pdf

def desenhar_parcela_boleto(canvas, boleto):
    width, height = A4
    altura_dinamica = 0

    # Logo Itau
    logo_path = "static/img/341.jpg"

    # path_bolecode = Constante.objects.using('lanmax').get(CodConst=207)

    # QRCode Bolecode
    # qrcode_bolecode = f'{path_bolecode.Constante}bolecode_{boleto['cod_pedido']}_{boleto['nosso_num']}.jpg'

    instr_local_pagto = InstrBol.objects.get(CodInstr=1)
    data_documento = datetime.now().strftime("%d/%m/%Y")

    str_numero = f'{boleto['ag']}{boleto['cc']}{boleto['carteira']}{boleto['nosso_num']}'
    dv = fncCalculoDV10(str_numero)
    nosso_num = f'{boleto['carteira']}/{boleto['nosso_num']}-{dv}'
    cod_barra = fncMontaCodBarras('341', 9, boleto['valor'], boleto['carteira'], boleto['nosso_num'], dv, boleto['ag'], boleto['cc'], boleto['digito'], boleto['vencimento'])
    linha_digitavel = fncLinhaDigitavel(cod_barra)

    valor_doc = locale.currency(boleto['valor'], grouping=True)

    instr1 = InstrBol.objects.get(CodInstr=2)
    instr2 = InstrBol.objects.get(CodInstr=3)
    instr3 = InstrBol.objects.get(CodInstr=4)
    instr4 = InstrBol.objects.get(CodInstr=5)
    instr5 = InstrBol.objects.get(CodInstr=6)
    instr6 = InstrBol.objects.get(CodInstr=7)

    valor_multa = f'{float(boleto['valor'])*0.00333:.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

    str_ficha_compensacao = ''

    # Loop para fazer 2 copias dos dados dos boletos
    for i in range(2):
        try:
            logo = ImageReader(logo_path)
            canvas.drawImage(logo, 9*mm, height - (22+altura_dinamica)*mm, width=7.2*mm, height=7.2*mm, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            print("Erro ao carregar logo:", e)

        canvas.setFont('Calibri-Bold', 9)
        canvas.drawString(17.5*mm, height - (20.5+altura_dinamica)*mm, 'Banco Itaú S.A.')

        canvas.setLineWidth(2)
        canvas.setStrokeColor(colors.gray)
        canvas.line(44*mm, height - (14.5+altura_dinamica)*mm, 44*mm, height - (21.5+altura_dinamica)*mm)

        canvas.setFillColor(colors.blue)
        canvas.setFont('Calibri-Bold', 14)
        canvas.drawString(45*mm, height - (20.5+altura_dinamica)*mm, '341-7')

        canvas.line(58*mm, height - (14.5+altura_dinamica)*mm, 58*mm, height - (21.5+altura_dinamica)*mm)

        canvas.setFillColor(colors.black)

        if i == 0:
            canvas.setFont('Calibri-Bold', 12)
            canvas.drawString(width - 42*mm, height - (20.5+altura_dinamica)*mm, 'Recibo do Pagador')
        else:
            canvas.setFont('Verdana', 12)
            canvas.drawString(60*mm, height - (20.5+altura_dinamica)*mm, linha_digitavel)

        # Borda lateral esquerda
        canvas.setLineWidth(0.5)
        canvas.setStrokeColor(colors.black)
        canvas.line(8.5*mm, height - (22.5+altura_dinamica)*mm, 8.5*mm, height - (120+altura_dinamica)*mm)

        # Borda meio
        canvas.line(width - 50*mm, height - (22.5+altura_dinamica)*mm, width - 50*mm, height - (103+altura_dinamica)*mm)

        # Borda lateral direita
        canvas.line(width - 7*mm, height - (22.5+altura_dinamica)*mm, width - 7*mm, height - (120+altura_dinamica)*mm)

        # Primeira linha tabela
        canvas.line(8.5*mm, height - (22.5+altura_dinamica)*mm, width - 7*mm, height - (22.5+altura_dinamica)*mm)

        canvas.setFont('Calibri', 8)
        canvas.drawString(9.5*mm, height - (25.5+altura_dinamica)*mm, 'Local de Pagamento')
        canvas.drawString(width - 49*mm, height - (25.5+altura_dinamica)*mm, 'Vencimento')

        canvas.setFont('Calibri-Bold', 10)
        canvas.drawString(13*mm, height - (30+altura_dinamica)*mm, instr_local_pagto.Instrucao)

        canvas.setFont('Calibri-Bold', 9)
        canvas.drawString(width - 24.5*mm, height - (31+altura_dinamica)*mm, boleto['vencimento'])

        # Fecha primeira linha
        canvas.line(8.5*mm, height - (31.5+altura_dinamica)*mm, width - 7*mm, height - (31.5+altura_dinamica)*mm)

        # Segunda linha
        canvas.setFont('Calibri', 8)
        canvas.drawString(9.5*mm, height - (34.5+altura_dinamica)*mm, 'Beneficiário')
        canvas.drawString(width - 49*mm, height - (34.5+altura_dinamica)*mm, 'Agência/Código Beneficiário')

        canvas.setFont('Calibri', 9)
        canvas.drawString(12*mm, height - (39.5+altura_dinamica)*mm, boleto['beneficiario'])
        canvas.drawString(width - 99*mm, height - (39.5+altura_dinamica)*mm, f'CPF/CNPJ: {boleto['cnpj_benef']}')
        canvas.drawString(width - 26.5*mm, height - (39.5+altura_dinamica)*mm, boleto['agencia_conta'])

        # Fecha segunda linha
        canvas.line(8.5*mm, height - (40.5+altura_dinamica)*mm, width - 7*mm, height - (40.5+altura_dinamica)*mm)

        # Terceira linha
        canvas.setFont('Calibri', 8)
        canvas.drawString(9.5*mm, height - (43+altura_dinamica)*mm, 'Data do Documento')
        canvas.line(37.5*mm, height - (40.5+altura_dinamica)*mm, 37.5*mm, height - (50+altura_dinamica)*mm)

        canvas.drawString(38.5*mm, height - (43+altura_dinamica)*mm, 'Número Documento')
        canvas.line(79*mm, height - (40.5+altura_dinamica)*mm, 79*mm, height - (50+altura_dinamica)*mm)

        canvas.drawString(80*mm, height - (43+altura_dinamica)*mm, 'Espécie Doc.')
        canvas.line(width - 107.5*mm, height - (40.5+altura_dinamica)*mm, width - 107.5*mm, height - (50+altura_dinamica)*mm)
        
        canvas.drawString(width - 106.5*mm, height - (43+altura_dinamica)*mm, 'Aceite')
        canvas.line(width - 92*mm, height - (40.5+altura_dinamica)*mm, width - 92*mm, height - (50+altura_dinamica)*mm)

        canvas.drawString(width - 91*mm, height - (43+altura_dinamica)*mm, 'Data Processamento')
        canvas.drawString(width - 49*mm, height - (43+altura_dinamica)*mm, 'Nosso Número')

        canvas.setFont('Calibri', 9)
        canvas.drawString(15*mm, height - (49+altura_dinamica)*mm, data_documento)

        canvas.drawString(48*mm, height - (49+altura_dinamica)*mm, boleto['num_doc'])
        canvas.drawString(88*mm, height - (49+altura_dinamica)*mm, 'DM')
        canvas.drawString(width - 102*mm, height - (49+altura_dinamica)*mm, 'N')
        canvas.drawString(width - 80*mm, height - (49+altura_dinamica)*mm, boleto['data_pedido'])

        canvas.drawString(width - 30*mm, height - (49+altura_dinamica)*mm, nosso_num)

        # Fecha terceira linha
        canvas.line(8.5*mm, height - (50+altura_dinamica)*mm, width - 7*mm, height - (50+altura_dinamica)*mm)

        # Quarta linha
        canvas.setFont('Calibri', 8)
        canvas.drawString(9.5*mm, height - (52.5+altura_dinamica)*mm, 'Uso do Banco')
        canvas.line(37.5*mm, height - (50+altura_dinamica)*mm, 37.5*mm, height - (59.5+altura_dinamica)*mm)

        canvas.drawString(38.5*mm, height - 52.5*mm, 'Carteira')
        canvas.line(59*mm, height - (50+altura_dinamica)*mm, 59*mm, height - (59.5+altura_dinamica)*mm)

        canvas.drawString(60*mm, height - 52.5*mm, 'Espécie')
        canvas.line(79*mm, height - (50+altura_dinamica)*mm, 79*mm, height - (59.5+altura_dinamica)*mm)

        canvas.drawString(80*mm, height - (52.5+altura_dinamica)*mm, 'Quantidade')
        canvas.line(width - 92*mm, height - (50+altura_dinamica)*mm, width - 92*mm, height - (59.5+altura_dinamica)*mm)

        canvas.drawString(width - 91*mm, height - (52.5+altura_dinamica)*mm, 'Valor')
        canvas.line(79*mm, height - (50+altura_dinamica)*mm, 79*mm, height - (59.5+altura_dinamica)*mm)

        canvas.drawString(width - 49*mm, height - (52.5+altura_dinamica)*mm, '(=) Valor do Documento')

        canvas.setFont('Calibri', 9)
        canvas.drawString(45*mm, height - (58.5+altura_dinamica)*mm, str(boleto['carteira']))
        canvas.drawString(67*mm, height - (58.5+altura_dinamica)*mm, 'R$')

        canvas.setFont('Calibri-Bold', 9)
        canvas.drawString(width - 45*mm, height - (58.5+altura_dinamica)*mm, valor_doc)

        # Fecha quarta linha
        canvas.line(8.5*mm, height - (59.5+altura_dinamica)*mm, width - 7*mm, height - (59.5+altura_dinamica)*mm)

        # Linha dos valores
        canvas.setFont('Calibri', 8)
        canvas.drawString(width - 49*mm, height - (62+altura_dinamica)*mm, '(-) Descontos/Abatimento')
        canvas.line(width - 50*mm, height - (68.5+altura_dinamica)*mm, width - 7*mm, height - (68.5+altura_dinamica)*mm)

        canvas.drawString(width - 49*mm, height - (71+altura_dinamica)*mm, '(-) Outras Deduções')
        canvas.line(width - 50*mm, height - (77+altura_dinamica)*mm, width - 7*mm, height - (77+altura_dinamica)*mm)

        canvas.drawString(width - 49*mm, height - (79.5+altura_dinamica)*mm, '(+) Mora/Multa')
        canvas.line(width - 50*mm, height - (85.5+altura_dinamica)*mm, width - 7*mm, height - (85.5+altura_dinamica)*mm)

        canvas.drawString(width - 49*mm, height - (88+altura_dinamica)*mm, '(+) Outros Acréscimos')
        canvas.line(width - 50*mm, height - (94+altura_dinamica)*mm, width - 7*mm, height - (94+altura_dinamica)*mm)

        canvas.drawString(width - 49*mm, height - (96.5+altura_dinamica)*mm, '(=) Valor Cobrado')

        # Instrucoes
        canvas.drawString(9.5*mm, height - (62+altura_dinamica)*mm, 'Instruções (Todas informações deste bloqueto são de exclusiva responsabilidade do cedente)')

        canvas.setFont('Calibri-Bold', 8)
        canvas.drawString(12*mm, height - (69+altura_dinamica)*mm, instr1.Instrucao)

        canvas.drawString(12*mm, height - (74+altura_dinamica)*mm, instr2.Instrucao)
        canvas.drawString(12*mm, height - (79+altura_dinamica)*mm, f'{instr3.Instrucao} {valor_multa} {instr4.Instrucao}')
        canvas.drawString(12*mm, height - (84+altura_dinamica)*mm, 'ATENÇÃO! ESTE É DE LIQUIDAÇÃO EXCLUSIVA POR COMPENSAÇÃO BANCÁRIA. O DEPÓSITO EM')
        canvas.drawString(12*mm, height - (87.5+altura_dinamica)*mm, 'C/C, TED OU TRANSFERÊNCIA, NÃO SÃO IDENTIFICADOS, PORTANTO NÃO QUITAM O(S)')
        canvas.drawString(12*mm, height - (91+altura_dinamica)*mm, 'DÉBITO(S).')

        canvas.setFont('Calibri', 8)
        canvas.drawString(9.5*mm, height - (102+altura_dinamica)*mm, 'Pagador/Avalista')

        # Bolecode se existir QRCode gerado
        # if Path(qrcode_bolecode).is_file():
        #     canvas.drawString(width - 75*mm, height - (69+altura_dinamica)*mm, instr6.Instrucao)

        #     imagem_qrcode_bolecode = ImageReader(qrcode_bolecode)
        #     canvas.drawImage(imagem_qrcode_bolecode, width - 83*mm, height - (102+altura_dinamica)*mm, width=32*mm, height=32*mm, preserveAspectRatio=True, mask='auto')

        # Linha pagador
        canvas.line(8.5*mm, height - (103+altura_dinamica)*mm, width - 7*mm, height - (103+altura_dinamica)*mm)

        canvas.setFont('Calibri', 8)
        canvas.drawString(9.5*mm, height - (106+altura_dinamica)*mm, 'Pagador')

        canvas.setFont('Calibri', 9)
        canvas.drawString(21*mm, height - (109+altura_dinamica)*mm, boleto['razao_social'])
        canvas.drawString(21*mm, height - (114+altura_dinamica)*mm, boleto['endereco'])
        canvas.drawString(21*mm, height - (119+altura_dinamica)*mm, boleto['cep'])
        canvas.drawString(44*mm, height - (119+altura_dinamica)*mm, boleto['cid_est'])
        canvas.drawString(105*mm, height - (119+altura_dinamica)*mm, f'CPF/CNPJ:  {boleto['cnpj']}')

        # Última linha
        canvas.line(8.5*mm, height - (120+altura_dinamica)*mm, width - 7*mm, height - (120+altura_dinamica)*mm)

        canvas.setFont('Calibri', 8)
        canvas.drawString(130*mm, height - (124+altura_dinamica)*mm, f'Autenticação Mecânica{str_ficha_compensacao}')

        if i == 0:
            canvas.setDash(8, 3)  # 4 pts traço, 3 pts espaço
            canvas.setLineWidth(0.1)
            canvas.line(8.5*mm, height-137*mm, width - 7*mm, height-137*mm)
            canvas.setDash([])  # volta para linha sólida depois

        str_ficha_compensacao = ' - Ficha de Compensação'
        altura_dinamica = 130

    barcode = I2of5(cod_barra, barWidth=0.27*mm, ratio=3.0, barHeight=13*mm, bearers=0, quiet=1, checksum=0)
    barcode.drawOn(canvas, 6*mm, height-265*mm)