from django.db import models
from usuarios.models import Usuario

class ReporteConfig(models.Model):
    """
    Configuración guardada de reportes para facilitar su regeneración.
    En lugar de guardar el archivo generado, solo guardamos los parámetros.
    """
    TIPOS = [
        ('ACCESOS', 'Accesos'),
        ('RESIDENTES', 'Residentes'),
        ('VIVIENDAS', 'Viviendas'),
        ('FINANCIERO', 'Financiero'),
        ('PERSONAL', 'Personal'),
    ]
    
    FORMATOS = [
        ('PDF', 'PDF'),
        ('CSV', 'CSV'),
        ('EXCEL', 'Excel'),
        ('HTML', 'HTML para visualización'),
    ]
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_desde = models.DateField()
    fecha_hasta = models.DateField()
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    filtros = models.JSONField(default=dict, blank=True, help_text="Filtros adicionales en formato JSON")
    formato_preferido = models.CharField(max_length=10, choices=FORMATOS, default='HTML')
    es_favorito = models.BooleanField(default=False, help_text="Marcar como reporte favorito para acceso rápido")
    ultima_generacion = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.tipo} - {self.fecha_creacion.strftime('%d/%m/%Y')}"
    
    class Meta:
        verbose_name = "Configuración de Reporte"
        verbose_name_plural = "Configuraciones de Reportes"
        ordering = ['-fecha_creacion']