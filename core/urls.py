from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='core_index'),
    path('monitoramento-nfe/', views.monitoramento_nfe, name='core_monitoramento_nfe'),
    path('nfe-email/', views.nfe_email, name='core_nfe_email'),
    path('faturados/', views.faturados, name='core_faturados'),
    re_path(r'^retransmitir/(?P<empresa_filial>-?\d+)/(?P<id_nfe>\d+)/$', views.retransmitir, name='core_retransmitir'),
    re_path(r'^(?P<empresa_filial>-?\d+)/(?P<id_nfe>\d+)/nfe-edit/$', views.nfe_edit, name='core_nfe_edit'),
]