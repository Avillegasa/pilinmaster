# Consolidación y mejoras para el modelo de Usuario con Roles, y su integración con Residente y Empleado
# usuarios/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from viviendas.models import Edificio

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class UsuarioManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('El nombre de usuario es obligatorio')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        user = self.create_user(username, email, password, **extra_fields)
        try:
            rol_admin = Rol.objects.get(nombre='Administrador')
        except Rol.DoesNotExist:
            rol_admin = Rol.objects.create(nombre='Administrador', descripcion='Rol por defecto para superusuarios')
        user.rol = rol_admin
        user.save()
        return user

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
    email_confirmado = models.BooleanField(default=False)

    objects = UsuarioManager()

    def clean(self):
        super().clean()
        if self.numero_documento and len(self.numero_documento) < 7:
            raise ValidationError('El número de documento debe tener al menos 7 caracteres')

    def save(self, *args, **kwargs):
        if self.is_superuser and not self.rol:
            try:
                rol_admin = Rol.objects.get(nombre='Administrador')
            except Rol.DoesNotExist:
                rol_admin = Rol.objects.create(nombre='Administrador', descripcion='Rol por defecto para superusuarios')
            self.rol = rol_admin
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.username}"

    @property
    def es_administrador(self):
        return self.rol and self.rol.nombre == 'Administrador'

    @property
    def es_gerente(self):
        return self.rol and self.rol.nombre == 'Gerente'

    @property
    def es_residente(self):
        return self.rol and self.rol.nombre == 'Residente'

    @property
    def es_vigilante(self):
        return self.rol and self.rol.nombre == 'Vigilante'

    @property
    def es_personal(self):
        return self.rol and self.rol.nombre == 'Personal'

    @property
    def es_visitante(self):
        return self.rol and self.rol.nombre == 'Visitante'
    
class ClientePotencial(models.Model):
    nombre_completo = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    ubicacion = models.CharField(max_length=255, blank=True)
    mensaje = models.TextField(blank=True)
    fecha_contacto = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_completo} - {self.email}"

    class Meta:
        verbose_name = "Cliente Potencial"
        verbose_name_plural = "Clientes Potenciales"
        permissions = [
            ("ver_cliente_potencial", "Puede ver clientes potenciales"),
        ]

class Gerente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='gerente')
    edificio = models.ForeignKey(Edificio, on_delete=models.PROTECT, related_name='gerentes')

    def clean(self):
        super().clean()
        # Validar que el rol del usuario sea "Gerente"
        if not self.usuario.rol or self.usuario.rol.nombre != 'Gerente':
            raise ValidationError('El usuario debe tener el rol "Gerente".')
        
        # Validar que el edificio fue seleccionado correctamente
        if not self.edificio:
            raise ValidationError("Debe seleccionar un edificio existente.")

    def __str__(self):
        return f"{self.usuario.get_full_name()} - Edificio: {self.edificio.nombre}"

    class Meta:
        verbose_name = "Gerente"
        verbose_name_plural = "Gerentes"

class Vigilante(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='vigilante')
    edificio = models.ForeignKey(Edificio, on_delete=models.PROTECT, related_name='vigilantes')

    def __str__(self):
        return f"Vigilante: {self.usuario.username} - {self.edificio.nombre}"
