from django.db import models
from usuarios.models import Usuario

class Edificio(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()
    pisos = models.PositiveIntegerField()
    fecha_construccion = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre

class Vivienda(models.Model):
    ESTADOS = [
        ('OCUPADO', 'Ocupado'),
        ('DESOCUPADO', 'Desocupado'),
        ('MANTENIMIENTO', 'En mantenimiento'),
    ]
    
    edificio = models.ForeignKey(Edificio, on_delete=models.CASCADE, related_name='viviendas')
    numero = models.CharField(max_length=10)
    piso = models.PositiveIntegerField()
    metros_cuadrados = models.DecimalField(max_digits=6, decimal_places=2)
    habitaciones = models.PositiveIntegerField(default=1)
    baños = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='DESOCUPADO')
    
    def __str__(self):
        return f"Vivienda {self.numero} - Piso {self.piso}"

class Residente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='residente')
    vivienda = models.ForeignKey(Vivienda, on_delete=models.SET_NULL, null=True, related_name='residentes')
    es_propietario = models.BooleanField(default=False)
    fecha_ingreso = models.DateField(auto_now_add=True)
    vehiculos = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name} - Vivienda {self.vivienda.numero if self.vivienda else 'No asignada'}"
