from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('api/', include('api.urls')),
    path('accounts/', include('accounts.urls')),
    path('lanmax/', include('lanmax.urls')),
    path('api-token-auth/', views.obtain_auth_token),
]
