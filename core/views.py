from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from .models import *

@login_required
def index(request):
    empresas = Empresa.objects.all()
    return render(request, 'core/index.html', {'empresas': empresas})

@login_required
@xframe_options_exempt
def boleto(request):
    pass

@csrf_exempt
def itau_webhook():
    pass
    