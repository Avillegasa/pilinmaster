from django.apps import AppConfig


class FinancieroConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'financiero'
    verbose_name = 'Gestión Financiera'
    
    def ready(self):
        """
        Importar las señales cuando la aplicación esté lista.
        """
        import financiero.signals  # noqa