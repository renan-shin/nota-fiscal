from django.urls import path, re_path
from . import views

urlpatterns = [
    path('consulta-status/<str:cod_empresa>', views.consulta_status, name='api_consulta_status'),
    path('consulta-empresa/<int:cod_pedido>', views.consulta_empresa, name='api_consulta_empresa'),
    re_path(r'^notas-fiscais/(?P<cod_empresa>-?\d+)?/?$', views.notas_fiscais, name='api_notas_fiscais'),
    re_path(r'^status-disponiveis/(?P<cod_empresa>-?\d+)?/?$', views.status_disponiveis, name='api_status_disponiveis'),
    path('gerar-pix/', views.gerar_pix, name='api_gerar_pix'),
    path('consulta-pix/<str:conta>/<str:inicio>/<str:fim>', views.consulta_pix, name='api_consulta_pix'),
    path('cancelar-pix/', views.cancelar_pix, name='api_cancelar_pix'),
    re_path(r'^gerar-orcamento-pdf/(?P<cod_pedido>-?\d+)/$', views.gerar_orcamento_pdf, name='api_gerar_orcamento_pdf'),
    re_path(r'^gerar-danfe/(?P<empresa_filial>-?\d+)/(?P<id_nfe>\d+)/$', views.gerar_danfe, name='api_gerar_danfe'),
    re_path(r'^gerar-boleto/(?P<empresa_filial>-?\d+)/(?P<id_nfe>\d+)/$', views.gerar_boleto, name='api_gerar_boleto'),
    re_path(r'^tem-boleto/(?P<empresa_filial>-?\d+)/(?P<id_nfe>\d+)/$', views.tem_boleto, name='api_tem_boleto'),
    re_path(r'^gerar-cupom/(?P<empresa_filial>-?\d+)/(?P<id_nfe>\d+)/$', views.gerar_cupom, name='api_gerar_cupom'),
    path('transmitir-nfe/', views.transmitir_nfe, name='api_transmitir_nfe'),
    path('transmitir-nfce/', views.transmitir_nfce, name='api_transmitir_nfce'),
    path('carta-correcao/', views.carta_correcao, name='api_carta_correcao'),
    path('cancelar-nfe/', views.cancelar_nfe, name='api_cancelar_nfe'),
    path('gerar-gnre/', views.gerar_gnre, name='api_gerar_gnre'),
    path('enviar-email-nfe/', views.enviar_email_nfe, name='api_enviar_email_nfe'),
]