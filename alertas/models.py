from django.db import models

class Alerta(models.Model):
    TIPO_CHOICES = [
        ('Incendio', 'Incendio'),
        ('Sismo', 'Sismo'),
        ('Seguridad', 'Seguridad'),
        ('Salud', 'Salud'),
        ('Aviso importante', 'Aviso importante'),
        ('Reunión', 'Reunión'),
    ]

    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    descripcion = models.TextField()
    usuario = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.usuario}"
