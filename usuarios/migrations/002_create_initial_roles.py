# usuarios/migrations/0002_create_initial_roles.py
# -*- coding: utf-8 -*-
from django.db import migrations

def create_initial_roles(apps, schema_editor):
    """
    Crear los roles iniciales del sistema Torre Segura
    ✅ CORRECCIÓN: Cambiar "Mantenimiento" por "Personal"
    """
    Rol = apps.get_model('usuarios', 'Rol')
    
    # Definir roles iniciales del sistema
    roles_iniciales = [
        {
            'nombre': 'Administrador',
            'descripcion': 'Acceso completo al sistema. Puede gestionar usuarios, configuraciones y todos los módulos.'
        },
        {
            'nombre': 'Gerente',
            'descripcion': 'Acceso administrativo con permisos para gestionar residentes, viviendas, personal y reportes.'
        },
        {
            'nombre': 'Personal',  # ✅ CORRECCIÓN: "Personal" en lugar de "Mantenimiento"
            'descripcion': 'Personal de mantenimiento, limpieza y servicios del condominio. Acceso a módulo de personal y asignaciones.'
        },
        {
            'nombre': 'Residente',
            'descripcion': 'Residente del condominio con acceso limitado a información de su vivienda y servicios básicos.'
        },
        {
            'nombre': 'Seguridad',
            'descripcion': 'Personal de seguridad con acceso al módulo de control de accesos y visitas.'
        }
    ]
    
    # Crear roles solo si no existen
    for rol_data in roles_iniciales:
        rol, created = Rol.objects.get_or_create(
            nombre=rol_data['nombre'],
            defaults={'descripcion': rol_data['descripcion']}
        )
        if created:
            print(f"✅ Rol creado: {rol.nombre}")
        else:
            # Actualizar descripción si el rol ya existe
            rol.descripcion = rol_data['descripcion']
            rol.save()
            print(f"🔄 Rol actualizado: {rol.nombre}")

def reverse_create_initial_roles(apps, schema_editor):
    """
    Función para revertir la migración (eliminar roles creados)
    NOTA: Solo elimina roles que no tengan usuarios asignados
    """
    Rol = apps.get_model('usuarios', 'Rol')
    
    roles_a_eliminar = ['Gerente', 'Personal', 'Residente', 'Seguridad']
    
    for nombre_rol in roles_a_eliminar:
        try:
            rol = Rol.objects.get(nombre=nombre_rol)
            # Solo eliminar si no tiene usuarios asignados
            if not rol.usuarios.exists():
                rol.delete()
                print(f"🗑️ Rol eliminado: {nombre_rol}")
            else:
                print(f"⚠️ No se puede eliminar el rol {nombre_rol} - tiene usuarios asignados")
        except Rol.DoesNotExist:
            print(f"ℹ️ Rol {nombre_rol} no existe")
    
    # NOTA: No eliminamos "Administrador" por seguridad del sistema

class Migration(migrations.Migration):
    
    dependencies = [
        ('usuarios', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(
            create_initial_roles,
            reverse_create_initial_roles,
            atomic=True
        ),
    ]