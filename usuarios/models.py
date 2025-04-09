from django.db import models
from django.contrib.auth.models import AbstractUser

class Rol(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    
    def __str__(self):
        return self.nombre

class Usuario(AbstractUser):
    TIPOS_DOCUMENTO = [
        ('DNI', 'DNI'),
        ('PASAPORTE', 'Pasaporte'),
        ('CEDULA', 'Cédula'),
    ]
    
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, related_name='usuarios')
    telefono = models.CharField(max_length=15, blank=True)
    tipo_documento = models.CharField(max_length=10, choices=TIPOS_DOCUMENTO, default='DNI')
    numero_documento = models.CharField(max_length=20, blank=True)
    foto = models.ImageField(upload_to='usuarios/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.username}"
