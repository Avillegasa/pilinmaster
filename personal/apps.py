from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError

class PersonalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'personal'

    def ready(self):
        try:
            from .models import Puesto
            puestos_definidos = [
                ("Jardinero", "Encargado del mantenimiento de áreas verdes"),
                ("Electricista", "Responsable de instalaciones eléctricas"),
                ("Fontanero", "Responsable de instalaciones sanitarias"),
                ("Pintor", "Realiza trabajos de pintura"),
                ("Otro", "Otros trabajos no clasificados")
            ]
            for nombre, descripcion in puestos_definidos:
                Puesto.objects.get_or_create(nombre=nombre, defaults={"descripcion": descripcion})
        except (OperationalError, ProgrammingError):
            pass
