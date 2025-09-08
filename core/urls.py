from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='core_index'),
    path('boleto/', views.boleto, name='core_boleto'),
    path('webhook/', views.itau_webhook, name='core_itau_webhook'),
]