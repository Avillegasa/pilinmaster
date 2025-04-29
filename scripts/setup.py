"""
Script para la configuración inicial del sistema:
- Crea la base de datos
- Aplica las migraciones
- Crea un superusuario
- Crea roles básicos
- Crea un edificio de ejemplo
- Genera viviendas de ejemplo
"""
import os
import sys
import django
from django.db import transaction

# Configurar entorno Django
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'condominio_app.settings')
django.setup()

from django.contrib.auth import get_user_model
from usuarios.models import Rol
from viviendas.models import Edificio, Vivienda, Residente, TipoResidente

Usuario = get_user_model()

def setup():
    print("Iniciando configuración del sistema...")
    
    try:
        with transaction.atomic():
            # Crear roles básicos
            print("Creando roles...")
            roles = {
                'Administrador': 'Control total del sistema',
                'Vigilante': 'Gestión de entradas y salidas',
                'Residente': 'Propietario o inquilino',
                'Gerente': 'Gestión administrativa'
            }
            
            for nombre, descripcion in roles.items():
                Rol.objects.get_or_create(nombre=nombre, defaults={'descripcion': descripcion})
            
            # Crear tipos de residentes
            print("Creando tipos de residentes...")
            tipos_residentes = {
                'Titular': {'descripcion': 'Habitante principal de la vivienda', 'es_propietario': True},
                'Dueño': {'descripcion': 'Propietario que no reside en el condominio', 'es_propietario': True},
                'Copropietario': {'descripcion': 'Habitante de la vivienda sin ser titular', 'es_propietario': True},
                'Menor': {'descripcion': 'Habitante menor de edad', 'es_propietario': False},
            }
            
            for nombre, datos in tipos_residentes.items():
                TipoResidente.objects.get_or_create(nombre=nombre, defaults=datos)
            
            # Crear superusuario (administrador)
            print("Creando superusuario...")
            if not Usuario.objects.filter(username='admin').exists():
                admin_user = Usuario.objects.create_superuser(
                    username='admin',
                    email='admin@condominio.com',
                    password='admin123',
                    first_name='Administrador',
                    last_name='Sistema',
                )
                admin_user.rol = Rol.objects.get(nombre='Administrador')
                admin_user.save()
            
            # Crear usuario vigilante
            print("Creando usuario vigilante...")
            if not Usuario.objects.filter(username='vigilante').exists():
                vigilante = Usuario.objects.create_user(
                    username='vigilante',
                    email='vigilante@condominio.com',
                    password='vigilante123',
                    first_name='Juan',
                    last_name='Pérez',
                )
                vigilante.rol = Rol.objects.get(nombre='Vigilante')
                vigilante.save()
            
            # Crear edificio de ejemplo
            print("Creando edificio de ejemplo...")
            edificio, created = Edificio.objects.get_or_create(
                nombre='Torre Aurora',
                defaults={
                    'direccion': 'Av. Principal #123, Ciudad',
                    'pisos': 10,
                    'fecha_construccion': '2018-01-01'
                }
            )
            
            # Crear viviendas de ejemplo
            if created:
                print("Creando viviendas de ejemplo...")
                for piso in range(1, 11):  # 10 pisos
                    for num in range(1, 5):  # 4 departamentos por piso
                        numero = f"{piso}0{num}"
                        Vivienda.objects.create(
                            edificio=edificio,
                            numero=numero,
                            piso=piso,
                            metros_cuadrados=85 + (5 * num),  # Variar tamaño
                            habitaciones=2 if num <= 2 else 3,
                            baños=1 if num == 1 else 2,
                            estado='DESOCUPADO'
                        )
            
            # Crear usuarios residentes y asignarlos a viviendas
            print("Creando residentes de ejemplo...")
            residentes = [
                {
                    'nombre': 'Carlos', 
                    'apellido': 'González', 
                    'username': 'carlos', 
                    'vivienda': '101', 
                    'tipo': 'Titular'
                },
                {
                    'nombre': 'María', 
                    'apellido': 'Rodríguez', 
                    'username': 'maria', 
                    'vivienda': '102', 
                    'tipo': 'Titular'
                },
                {
                    'nombre': 'Jorge', 
                    'apellido': 'Fernández', 
                    'username': 'jorge', 
                    'vivienda': '201', 
                    'tipo': 'Copropietario'
                },
                {
                    'nombre': 'Ana', 
                    'apellido': 'López', 
                    'username': 'ana', 
                    'vivienda': '301', 
                    'tipo': 'Dueño'
                },
                {
                    'nombre': 'Pedro', 
                    'apellido': 'Ramírez', 
                    'username': 'pedro', 
                    'vivienda': '102', 
                    'tipo': 'Menor'
                }
            ]
            
            for r in residentes:
                if not Usuario.objects.filter(username=r['username']).exists():
                    usuario = Usuario.objects.create_user(
                        username=r['username'],
                        email=f"{r['username']}@condominio.com",
                        password=f"{r['username']}123",
                        first_name=r['nombre'],
                        last_name=r['apellido'],
                    )
                    usuario.rol = Rol.objects.get(nombre='Residente')
                    usuario.save()
                    
                    vivienda = Vivienda.objects.get(edificio=edificio, numero=r['vivienda'])
                    vivienda.estado = 'OCUPADO'
                    vivienda.save()
                    
                    tipo_residente = TipoResidente.objects.get(nombre=r['tipo'])
                    
                    Residente.objects.create(
                        usuario=usuario,
                        vivienda=vivienda,
                        tipo_residente=tipo_residente,
                        es_propietario=tipo_residente.es_propietario,
                        vehiculos=1 if tipo_residente.nombre in ['Titular', 'Dueño'] else 0,
                        activo=True
                    )
            
            print("Configuración inicial completada con éxito.")
            
    except Exception as e:
        print(f"Error durante la configuración: {e}")
        raise

if __name__ == "__main__":
    setup()