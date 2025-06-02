from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from usuarios.models import Usuario
from viviendas.models import Edificio, Vivienda

class Puesto(models.Model):
    """
    Modelo para definir los diferentes puestos de trabajo del personal
    del condominio, como conserje, jardinero, técnico de mantenimiento, etc.
    """
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    requiere_especializacion = models.BooleanField(default=False)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Puesto"
        verbose_name_plural = "Puestos"
        ordering = ['nombre']

class Empleado(models.Model):
    """
    Modelo para gestionar los empleados que trabajan en el condominio.
    Se relaciona con el modelo Usuario para gestionar la autenticación.
    """
    TIPOS_CONTRATO = [
        ('PERMANENTE', 'Permanente'),
        ('TEMPORAL', 'Temporal'),
        ('EXTERNO', 'Proveedor Externo'),
    ]
    
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='empleado')
    puesto = models.ForeignKey(Puesto, on_delete=models.PROTECT, related_name='empleados')
    fecha_contratacion = models.DateField()
    tipo_contrato = models.CharField(max_length=15, choices=TIPOS_CONTRATO, default='PERMANENTE')
    salario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    contacto_emergencia = models.CharField(max_length=150, blank=True)
    telefono_emergencia = models.CharField(max_length=15, blank=True)
    especialidad = models.CharField(max_length=100, blank=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name} - {self.puesto.nombre}"
    
    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ['usuario__last_name', 'usuario__first_name']

class Asignacion(models.Model):
    """
    Modelo para gestionar las asignaciones de trabajo a los empleados.
    Puede ser una tarea puntual o una responsabilidad recurrente.
    """
    TIPOS_ASIGNACION = [
        ('TAREA', 'Tarea puntual'),
        ('RESPONSABILIDAD', 'Responsabilidad recurrente'),
    ]
    
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROGRESO', 'En progreso'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    PRIORIDADES = [
        (1, 'Baja'),
        (2, 'Normal'),
        (3, 'Alta'),
        (4, 'Urgente'),
    ]
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='asignaciones')
    tipo = models.CharField(max_length=20, choices=TIPOS_ASIGNACION)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_asignacion = models.DateField(auto_now_add=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    edificio = models.ForeignKey(Edificio, on_delete=models.CASCADE, related_name='asignaciones', null=True, blank=True)
    vivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE, related_name='asignaciones', null=True, blank=True)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='PENDIENTE')
    prioridad = models.IntegerField(choices=PRIORIDADES, default=2)
    notas = models.TextField(blank=True)
    asignado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='asignaciones_creadas')
    
    def __str__(self):
        return f"{self.titulo} - {self.empleado}"
    
    class Meta:
        verbose_name = "Asignación"
        verbose_name_plural = "Asignaciones"
        ordering = ['-fecha_asignacion', '-prioridad']

class ComentarioAsignacion(models.Model):
    """
    Modelo para registrar comentarios sobre las asignaciones,
    ya sea por parte del empleado o de los administradores.
    """
    asignacion = models.ForeignKey(Asignacion, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    comentario = models.TextField()
    
    def __str__(self):
        return f"Comentario de {self.usuario} en {self.asignacion.titulo}"
    
    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ['-fecha']

# Señal para sincronizar el estado del empleado cuando cambia el estado del usuario
@receiver(post_save, sender=Usuario)
def update_empleado_status(sender, instance, **kwargs):
    try:
        if hasattr(instance, 'empleado'):
            if instance.empleado.activo != instance.is_active:
                instance.empleado.activo = instance.is_active
                instance.empleado.save(update_fields=['activo'])
    except Exception:
        pass  # Si no hay empleado asociado, no hacer nada