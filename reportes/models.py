from django.db import models
from usuarios.models import Usuario

class Reporte(models.Model):
    TIPOS = [
        ('ACCESOS', 'Accesos'),
        ('RESIDENTES', 'Residentes'),
        ('VIVIENDAS', 'Viviendas'),
        ('FINANCIERO', 'Financiero'),
    ]
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_desde = models.DateField()
    fecha_hasta = models.DateField()
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    archivo = models.FileField(upload_to='reportes/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.tipo} - {self.fecha_creacion.strftime('%d/%m/%Y')}"