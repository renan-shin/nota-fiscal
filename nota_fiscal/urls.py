from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('nfe/', include('nfe_util.urls')),
    path('api/', include('api.urls')),
    path('accounts/', include('accounts.urls')),
    path('lanmax/', include('lanmax.urls')),
    path('mdfe/', include('mdfe_util.urls')),
    path('api-token-auth/', views.obtain_auth_token),
]
