# viviendas/models.py - VERSIÓN CORREGIDA
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.conf import settings

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
    
    def save(self, *args, **kwargs):
        if not self.activo and self.estado != 'BAJA':
            self.estado = 'BAJA'
        if self.estado == 'DESOCUPADO':
            self.activo = True
        super().save(*args, **kwargs)


class Residente(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='residente')
    vivienda = models.ForeignKey(Vivienda, on_delete=models.SET_NULL, null=True, related_name='residentes')
    fecha_ingreso = models.DateField(auto_now_add=True)
    vehiculos = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True, 
        help_text="Indica si el residente actualmente vive o está relacionado con la vivienda")
    es_propietario = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # ✅ Evitar recursión: solo actualizar si es necesario
        vivienda_anterior = None
        
        # Si el objeto ya existe, obtener la vivienda anterior
        if self.pk:
            try:
                vivienda_anterior = Residente.objects.get(pk=self.pk).vivienda
            except Residente.DoesNotExist:
                pass
        
        # Sincronizar con el estado del usuario
        self.activo = self.usuario.is_active
        
        # Guardar el residente primero
        super().save(*args, **kwargs)
        
        # ✅ Actualizar estados de vivienda SIN recursión
        if vivienda_anterior and vivienda_anterior != self.vivienda:
            # Liberar vivienda anterior
            Vivienda.objects.filter(pk=vivienda_anterior.pk).update(estado='DESOCUPADO')
        
        if self.vivienda and self.activo:
            # Ocupar nueva vivienda (solo si el residente está activo)
            Vivienda.objects.filter(pk=self.vivienda.pk).update(estado='OCUPADO')
        elif self.vivienda and not self.activo:
            # Si el residente se desactiva, liberar la vivienda
            Vivienda.objects.filter(pk=self.vivienda.pk).update(estado='DESOCUPADO')
    
    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name} - Vivienda {self.vivienda.numero if self.vivienda else 'No asignada'}"


# ✅ SEÑALES OPTIMIZADAS - Sin recursión infinita
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def update_residente_status(sender, instance, created, **kwargs):
    """Sincronizar estado del residente cuando cambia el usuario"""
    if not created and hasattr(instance, 'residente'):
        residente = instance.residente
        if residente.activo != instance.is_active:
            # ✅ Usar update() para evitar señales en cascada
            Residente.objects.filter(pk=residente.pk).update(activo=instance.is_active)
            
            # Si se desactiva el usuario, liberar la vivienda
            if not instance.is_active and residente.vivienda:
                Vivienda.objects.filter(pk=residente.vivienda.pk).update(estado='DESOCUPADO')
            # Si se reactiva el usuario, ocupar la vivienda
            elif instance.is_active and residente.vivienda:
                Vivienda.objects.filter(pk=residente.vivienda.pk).update(estado='OCUPADO')


@receiver(pre_delete, sender=Residente)
def liberar_vivienda_al_eliminar_residente(sender, instance, **kwargs):
    """Liberar vivienda cuando se elimina un residente"""
    if instance.vivienda:
        Vivienda.objects.filter(pk=instance.vivienda.pk).update(estado='DESOCUPADO')