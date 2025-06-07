from django.db import models
from django.conf import settings

class Alerta(models.Model):
    TIPOS_ALERTA = [
        ('Incendio', 'Incendio'),
        ('Sismo', 'Sismo'),
        ('Seguridad', 'Seguridad'),
        ('Salud', 'Salud'),
        ('Aviso importante', 'Aviso importante'),
        ('Reunión', 'Reunión'),
    ]
    
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('resuelto', 'Resuelto'),
    ]
    
    tipo = models.CharField(max_length=50, choices=TIPOS_ALERTA)
    descripcion = models.TextField()
    enviado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='alertas_enviadas')
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    atendido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='alertas_atendidas')
    fecha_atencion = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.tipo} - {self.enviado_por.username} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"