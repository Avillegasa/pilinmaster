from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver

class Rol(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    
    def clean(self):
        super().clean()
        # ✅ PROTECCIÓN: Normalizar nombre del rol
        if self.nombre:
            self.nombre = self.nombre.strip().title()
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"

class Usuario(AbstractUser):
    TIPOS_DOCUMENTO = [
        ('CEDULA', 'Cédula de Identidad'),  # ✅ CORRECCIÓN: Solo cédula como solicitado
    ]
    
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, related_name='usuarios')
    telefono = models.CharField(max_length=15, blank=True)
    tipo_documento = models.CharField(max_length=10, choices=TIPOS_DOCUMENTO, default='CEDULA')
    numero_documento = models.CharField(
        max_length=20, 
        blank=True,
        help_text="Solo números. Mínimo 7 caracteres."
    )
    foto = models.ImageField(upload_to='usuarios/', blank=True, null=True)

    def clean(self):
        super().clean()
        
        # ✅ VALIDACIÓN: Número de documento solo números
        if self.numero_documento:
            # Limpiar espacios y caracteres no numéricos
            numero_limpio = ''.join(filter(str.isdigit, self.numero_documento))
            
            if not numero_limpio:
                raise ValidationError({
                    'numero_documento': 'El número de documento debe contener solo números.'
                })
            
            if len(numero_limpio) < 7:
                raise ValidationError({
                    'numero_documento': 'El número de documento debe tener al menos 7 dígitos.'
                })
            
            # Actualizar con el número limpio
            self.numero_documento = numero_limpio
        
        # ✅ PROTECCIÓN CRÍTICA: Validar que no se desactive el último administrador
        if self.pk and not self.is_active and self.rol and self.rol.nombre == 'Administrador':
            otros_admins_activos = Usuario.objects.filter(
                rol__nombre='Administrador',
                is_active=True
            ).exclude(pk=self.pk).exists()
            
            if not otros_admins_activos:
                raise ValidationError({
                    'is_active': 'No se puede desactivar el último usuario Administrador del sistema.'
                })
    
    def save(self, *args, **kwargs):
        # ✅ PROTECCIÓN ADICIONAL: Verificar antes de guardar
        if self.pk:  # Solo si es actualización
            try:
                usuario_anterior = Usuario.objects.get(pk=self.pk)
                
                # Si se está intentando desactivar un administrador
                if (usuario_anterior.is_active and not self.is_active and 
                    self.rol and self.rol.nombre == 'Administrador'):
                    
                    # Contar otros administradores activos
                    otros_admins = Usuario.objects.filter(
                        rol__nombre='Administrador',
                        is_active=True
                    ).exclude(pk=self.pk).count()
                    
                    if otros_admins == 0:
                        raise ValidationError(
                            "OPERACIÓN DENEGADA: No se puede desactivar el último Administrador del sistema."
                        )
            except Usuario.DoesNotExist:
                pass  # Usuario nuevo, proceder normalmente
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.username}"
    
    @property
    def es_administrador(self):
        """Método auxiliar para verificar si el usuario es administrador"""
        return self.rol and self.rol.nombre == 'Administrador'
    
    @property
    def puede_ser_modificado(self):
        """Método auxiliar para verificar si el usuario puede ser modificado"""
        return not self.es_administrador
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

# ✅ SEÑALES DE PROTECCIÓN
@receiver(pre_save, sender=Usuario)
def proteger_administrador_pre_save(sender, instance, **kwargs):
    """
    Señal que se ejecuta antes de guardar un usuario
    Protege contra modificaciones no autorizadas de administradores
    """
    if instance.pk:  # Solo para actualizaciones
        try:
            usuario_anterior = Usuario.objects.get(pk=instance.pk)
            
            # Si el usuario era administrador y se está intentando cambiar su rol
            if (usuario_anterior.rol and usuario_anterior.rol.nombre == 'Administrador' and
                (not instance.rol or instance.rol.nombre != 'Administrador')):
                
                # Contar otros administradores
                otros_admins = Usuario.objects.filter(
                    rol__nombre='Administrador'
                ).exclude(pk=instance.pk).count()
                
                if otros_admins == 0:
                    raise ValidationError(
                        "No se puede cambiar el rol del último Administrador del sistema."
                    )
                    
        except Usuario.DoesNotExist:
            pass

@receiver(pre_delete, sender=Usuario)
def proteger_administrador_pre_delete(sender, instance, **kwargs):
    """
    Señal que se ejecuta antes de eliminar un usuario
    Protege contra eliminación de administradores
    """
    if instance.rol and instance.rol.nombre == 'Administrador':
        # Contar otros administradores
        otros_admins = Usuario.objects.filter(
            rol__nombre='Administrador'
        ).exclude(pk=instance.pk).count()
        
        if otros_admins == 0:
            raise ValidationError(
                "OPERACIÓN DENEGADA: No se puede eliminar el último Administrador del sistema."
            )
        else:
            raise ValidationError(
                "OPERACIÓN DENEGADA: No se pueden eliminar usuarios con rol de Administrador por razones de seguridad."
            )

@receiver(pre_delete, sender=Rol)
def proteger_rol_administrador(sender, instance, **kwargs):
    """
    Señal que se ejecuta antes de eliminar un rol
    Protege el rol de Administrador
    """
    if instance.nombre == 'Administrador':
        raise ValidationError(
            "OPERACIÓN DENEGADA: No se puede eliminar el rol 'Administrador' por razones de seguridad del sistema."
        )