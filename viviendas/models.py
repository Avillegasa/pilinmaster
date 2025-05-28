from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from usuarios.models import Usuario

class Edificio(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()
    pisos = models.PositiveIntegerField()
    fecha_construccion = models.DateField(blank=True, null=True)
    # ✅ NUEVOS CAMPOS (agregar estos):
    activo = models.BooleanField(default=True, help_text="Indica si el edificio está activo o ha sido dado de baja")
    fecha_baja = models.DateField(null=True, blank=True, help_text="Fecha en la que se dio de baja el edificio")
    motivo_baja = models.TextField(blank=True, null=True, help_text="Motivo por el cual se dio de baja el edificio")
    
    # ✅ MÉTODO SAVE (agregar este método completo):
    def save(self, *args, **kwargs):
        if not self.activo and self.fecha_baja is None:
            from django.utils import timezone
            self.fecha_baja = timezone.now().date()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nombre

class Vivienda(models.Model):
    ESTADOS = [
        ('OCUPADO', 'Ocupado'),
        ('DESOCUPADO', 'Desocupado'),
        ('MANTENIMIENTO', 'En mantenimiento'),
        ('BAJA', 'Dado de baja'),
    ]
    
    edificio = models.ForeignKey(Edificio, on_delete=models.CASCADE, related_name='viviendas')
    numero = models.CharField(max_length=10)
    piso = models.PositiveIntegerField()
    metros_cuadrados = models.DecimalField(max_digits=6, decimal_places=2)
    habitaciones = models.PositiveIntegerField(default=1)
    baños = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='DESOCUPADO')
    activo = models.BooleanField(default=True, help_text="Indica si la vivienda está activa o ha sido dada de baja")
    fecha_baja = models.DateField(null=True, blank=True, help_text="Fecha en la que se dio de baja la vivienda")
    motivo_baja = models.TextField(blank=True, null=True, help_text="Motivo por el cual se dio de baja la vivienda")
    
    def __str__(self):
        return f"Vivienda {self.numero} - Piso {self.piso}"
    
    # Guardar método para asegurar que la vivienda dada de baja tenga estado BAJA
    def save(self, *args, **kwargs):
        if not self.activo and self.estado != 'BAJA':
            self.estado = 'BAJA'
        super().save(*args, **kwargs)

class Residente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='residente')
    vivienda = models.ForeignKey(Vivienda, on_delete=models.SET_NULL, null=True, related_name='residentes')
    fecha_ingreso = models.DateField(auto_now_add=True)
    vehiculos = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True, 
        help_text="Indica si el residente actualmente vive o está relacionado con la vivienda")
    es_propietario = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # Sincronizar activo con is_active del usuario
        self.activo = self.usuario.is_active
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name} - Vivienda {self.vivienda.numero if self.vivienda else 'No asignada'}"

# Señal para sincronizar el estado del residente cuando cambia el estado del usuario
@receiver(post_save, sender=Usuario)
def update_residente_status(sender, instance, **kwargs):
    try:
        if hasattr(instance, 'residente'):
            if instance.residente.activo != instance.is_active:
                instance.residente.activo = instance.is_active
                instance.residente.save(update_fields=['activo'])
    except Exception:
        pass  # Si no hay residente asociado, no hacer nada