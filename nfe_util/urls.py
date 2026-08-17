from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='nfe_util_index'),
    path('monitoramento/', views.monitoramento_nfe, name='nfe_util_monitoramento'),
    path('email/', views.email, name='nfe_util_email'),
    path('faturados/', views.faturados, name='nfe_util_faturados'),
    path('gerar-chave-acesso/', views.gerar_chave_acesso, name='nfe_util_gerar_chave_acesso'),
    re_path(r'^retransmitir/(?P<empresa_filial>-?\d+)/(?P<id_nfe>\d+)/$', views.retransmitir, name='nfe_util_retransmitir'),
    re_path(r'^(?P<empresa_filial>-?\d+)/(?P<id_nfe>\d+)/edit/$', views.edit, name='nfe_util_edit'),
]