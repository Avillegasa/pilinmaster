
# Script de corrección automática
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'condominio_app.settings')
django.setup()

from usuarios.models import Usuario, Rol
from viviendas.models import Vivienda, Residente

print("🔧 EJECUTANDO CORRECCIONES AUTOMÁTICAS...")

# 1. Crear roles faltantes
roles_requeridos = ['Administrador', 'Gerente', 'Residente', 'Personal', 'Vigilante']
for rol_nombre in roles_requeridos:
    rol, created = Rol.objects.get_or_create(nombre=rol_nombre)
    if created:
        print(f"✅ Rol '{rol_nombre}' creado")

# 2. Asignar rol por defecto a usuarios sin rol
rol_residente = Rol.objects.get(nombre='Residente')
usuarios_sin_rol = Usuario.objects.filter(rol__isnull=True)
for usuario in usuarios_sin_rol:
    usuario.rol = rol_residente
    usuario.save()
    print(f"✅ Rol 'Residente' asignado a {usuario.username}")

# 3. Corregir estados de vivienda
viviendas_ocupadas = Vivienda.objects.filter(estado='OCUPADO')
for vivienda in viviendas_ocupadas:
    residentes_activos = vivienda.residentes.filter(activo=True).count()
    if residentes_activos == 0:
        vivienda.estado = 'DESOCUPADO'
        vivienda.save()
        print(f"✅ Vivienda {vivienda} marcada como DESOCUPADO")

print("🎉 Correcciones completadas!")
