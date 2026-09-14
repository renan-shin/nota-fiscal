from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from nfe_util.models import *
from .models import *
from lanmax.models import *
from django.apps import apps
from django.contrib import messages
from django.db.models import Q

# Create your views here.
@login_required
def index(request):
    empresas = Empresa.objects.filter(Tabela_MDFe__isnull=False)
    return render(request, 'mdfe_util/index.html', {'empresas': empresas})

@login_required
def mdfe_edit(request, empresa_filial, id_mdfe):
    try:
        empresa = Empresa.objects.get(EmpresaFilial=empresa_filial)
        nome_tabela = apps.get_model('mdfe_util', empresa.Tabela_MDFe)
    except Empresa.DoesNotExist:
        messages.error(request, 'Empresa não encontrada!')
        return redirect('mdfe_index')

    try:
        mdfe = nome_tabela.objects.get(id_mdfe=id_mdfe)
    except nome_tabela.DoesNotExist:
        messages.error(request, 'Manifesto não encontrado!')
        return redirect('mdfe_index')

    chaves_nfe = MDFe_ChaveNFe.objects.filter(id_mdfe=mdfe.id_mdfe, ide_serie=mdfe.ide_serie)
    percurso = MDFe_Percursos.objects.filter(id_mdfe=mdfe.id_mdfe, ide_serie=mdfe.ide_serie).order_by('ordem')
    motoristas = MDFe_Motoristas.objects.all().order_by('nome')
    veiculos = MDFe_Veiculos.objects.filter(
        Q(EmpresaFilial=empresa_filial) | Q(EmpresaFilial__isnull=True)
    ).order_by('marca', 'modelo')
    
    ufs = TabUF.objects.all().order_by('UF')

    if request.method == 'GET':
        return render(request,
            'mdfe_util/edit.html',
            {
                'empresa': empresa,
                'mdfe': mdfe,
                'chaves_nfe': chaves_nfe,
                'percurso': percurso,
                'motoristas': motoristas,
                'veiculos': veiculos,
                'ufs': ufs
            })

    if request.method == 'POST':
        motorista = request.POST.get('motorista', '')
        veiculo = request.POST.get('veiculo', '')
        uf_inicio = request.POST.get('uf_inicio', '')
        uf_fim = request.POST.get('uf_fim', '')

        if mdfe.status != 'MDFe não enviada':
            messages.error(request, 'Opção de envio de e-mail inválida!')

            return render(request, 'mdfe_util/edit.html', {
                'empresa': empresa,
                'mdfe': mdfe,
                'chaves_nfe': chaves_nfe,
                'percurso': percurso,
                'motoristas': motoristas,
                'veiculos': veiculos,
                'ufs': ufs,
                'form': request.POST
            })

        if motorista is None or motorista == '':
            messages.error(request, 'Motorista não informado!')
            return render(request, 'mdfe_util/edit.html', {
                'empresa': empresa,
                'mdfe': mdfe,
                'chaves_nfe': chaves_nfe,
                'percurso': percurso,
                'motoristas': motoristas,
                'veiculos': veiculos,
                'ufs': ufs,
                'form': request.POST
            })

        if veiculo is None or veiculo == '':
            messages.error(request, 'Veículo não informado!')
            return render(request, 'mdfe_util/edit.html', {
                'empresa': empresa,
                'mdfe': mdfe,
                'chaves_nfe': chaves_nfe,
                'percurso': percurso,
                'motoristas': motoristas,
                'veiculos': veiculos,
                'ufs': ufs,
                'form': request.POST
            })

        try:
            mdfe_motorista = MDFe_Motoristas.objects.get(id=motorista)
        except MDFe_Motoristas.DoesNotExist:
            messages.error(request, 'Motorista não encontrado!')

            return render(request, 'mdfe_util/edit.html', {
                'empresa': empresa,
                'mdfe': mdfe,
                'chaves_nfe': chaves_nfe,
                'percurso': percurso,
                'motoristas': motoristas,
                'veiculos': veiculos,
                'ufs': ufs,
                'form': request.POST
            })

        try:
            mdfe_veiculo = MDFe_Veiculos.objects.get(id=veiculo)
        except MDFe_Veiculos.DoesNotExist:
            messages.error(request, 'Veículo não encontrado!')
            
            return render(request, 'mdfe_util/edit.html', {
                'empresa': empresa,
                'mdfe': mdfe,
                'chaves_nfe': chaves_nfe,
                'percurso': percurso,
                'motoristas': motoristas,
                'veiculos': veiculos,
                'ufs': ufs,
                'form': request.POST
            })

        mdfe.ide_UFIni = uf_inicio
        mdfe.ide_UFFim = uf_fim
        mdfe.id_condutor = mdfe_motorista
        mdfe.id_veiculo = mdfe_veiculo
        mdfe.save()
        mdfe.refresh_from_db()
        messages.success(request, 'Dados salvos com sucesso!')

        return render(request, 'mdfe_util/edit.html', {
            'empresa': empresa,
            'mdfe': mdfe,
            'chaves_nfe': chaves_nfe,
            'percurso': percurso,
            'motoristas': motoristas,
            'veiculos': veiculos,
            'ufs': ufs,
            'form': request.POST
        })