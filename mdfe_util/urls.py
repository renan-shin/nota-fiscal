from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='mdfe_index'),
    re_path(r'^(?P<empresa_filial>-?\d+)/(?P<id_mdfe>\d+)/edit/$', views.mdfe_edit, name='mdfe_edit'),
]