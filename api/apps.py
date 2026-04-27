from django.apps import AppConfig

def ready(self):
    import core.signals

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
