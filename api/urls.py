from django.urls import path, re_path
from . import views

urlpatterns = [
    path('consulta-status/<str:cod_empresa>', views.consulta_status, name='api_consulta_status'),
    path('consulta-empresa/<int:cod_pedido>', views.consulta_empresa, name='api_consulta_empresa'),
    re_path(r'^notas-fiscais/(?P<cod_empresa>-?\d+)?/?$', views.notas_fiscais, name='api_notas_fiscais'),
    re_path(r'^status-disponiveis/(?P<cod_empresa>-?\d+)?/?$', views.status_disponiveis, name='api_status_disponiveis'),
    path('gerar-pix/', views.gerar_pix, name='api_gerar_pix'),
    path('consulta-pix/<str:conta>', views.consulta_pix, name='api_consulta_pix'),
    path('cancelar-pix/', views.cancelar_pix, name='api_cancelar_pix'),
    re_path(r'^gerar-danfe/(?P<empresa_filial>-?\d+)/(?P<id_nfe>\d+)/$', views.gerar_danfe, name='api_gerar_danfe'),
    path('gerar-boleto/<int:cod_pedido>', views.gerar_boleto, name='api_gerar_boleto'),
]