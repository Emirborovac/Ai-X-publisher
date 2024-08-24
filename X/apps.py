from django.apps import AppConfig

class XConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'X'

    def ready(self):
        import X.signals  # Import the signals module to connect signal handlers
