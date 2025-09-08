from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='accounts_login'),
    path('logout/', views.logout, name='accounts_logout'),
]