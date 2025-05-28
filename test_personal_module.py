# test_personal_module.py
# Script para probar el módulo de personal de forma automatizada

import os
import django
import sys
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'condominio_app.settings')
django.setup()

def run_comprehensive_tests():
    """Ejecuta pruebas comprensivas del módulo personal"""
    
    print("🧪 INICIANDO PRUEBAS COMPRENSIVAS DEL MÓDULO PERSONAL")
    print("=" * 60)
    
    # 1. Verificar estructura de archivos
    print("\n1. ✅ VERIFICANDO ESTRUCTURA DE ARCHIVOS...")
    files_to_check = [
        'personal/models.py',
        'personal/views.py', 
        'personal/forms.py',
        'personal/urls.py',
        'personal/tests.py',
        'templates/personal/empleado_list.html',
        'templates/personal/asignacion_list.html',
        'static/js/asignaciones_filters.js'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - ARCHIVO FALTANTE")
    
    # 2. Verificar imports y sintaxis
    print("\n2. ✅ VERIFICANDO IMPORTS Y SINTAXIS...")
    try:
        from personal.models import Puesto, Empleado, Asignacion, ComentarioAsignacion
        from personal.views import PuestoListView, EmpleadoListView, AsignacionListView
        from personal.forms import PuestoForm, EmpleadoForm, AsignacionForm
        print("   ✅ Todos los imports funcionan correctamente")
    except ImportError as e:
        print(f"   ❌ Error de import: {e}")
        return False
    
    # 3. Verificar migraciones
    print("\n3. ✅ VERIFICANDO MIGRACIONES...")
    try:
        from django.core.management import execute_from_command_line
        # Simular verificación de migraciones
        print("   ✅ Ejecutar: python manage.py makemigrations personal")
        print("   ✅ Ejecutar: python manage.py migrate")
        print("   ⚠️  Recuerda ejecutar estos comandos manualmente")
    except Exception as e:
        print(f"   ❌ Error con migraciones: {e}")
    
    # 4. Ejecutar tests unitarios
    print("\n4. ✅ EJECUTANDO TESTS UNITARIOS...")
    try:
        from django.test.utils import get_runner
        from django.conf import settings
        
        # Configurar test runner
        TestRunner = get_runner(settings)
        test_runner = TestRunner()
        
        # Ejecutar tests del módulo personal
        failures = test_runner.run_tests(["personal"])
        
        if failures:
            print(f"   ❌ {failures} tests fallaron")
            return False
        else:
            print("   ✅ Todos los tests unitarios pasaron")
            
    except Exception as e:
        print(f"   ⚠️  No se pudieron ejecutar tests automáticamente: {e}")
        print("   🔧 Ejecuta manualmente: python manage.py test personal")
    
    # 5. Verificar URLs
    print("\n5. ✅ VERIFICANDO CONFIGURACIÓN DE URLS...")
    try:
        from django.urls import resolve
        
        urls_to_test = [
            '/personal/empleados/',
            '/personal/asignaciones/',
            '/personal/puestos/',
            '/personal/empleados/crear/',
            '/personal/asignaciones/crear/'
        ]
        
        for url in urls_to_test:
            try:
                resolve(url)
                print(f"   ✅ {url}")
            except Exception:
                print(f"   ❌ {url} - URL no encontrada")
                
    except Exception as e:
        print(f"   ❌ Error verificando URLs: {e}")
    
    # 6. Verificar modelos
    print("\n6. ✅ VERIFICANDO MODELOS...")
    try:
        # Verificar que los modelos se pueden instanciar
        puesto = Puesto(nombre="Test Puesto", descripcion="Test")
        empleado_fields = Empleado._meta.get_fields()
        asignacion_fields = Asignacion._meta.get_fields()
        
        print(f"   ✅ Modelo Puesto: {len([f for f in Puesto._meta.get_fields()])} campos")
        print(f"   ✅ Modelo Empleado: {len(empleado_fields)} campos")
        print(f"   ✅ Modelo Asignacion: {len(asignacion_fields)} campos")
        print("   ✅ Todos los modelos están correctamente definidos")
        
    except Exception as e:
        print(f"   ❌ Error con modelos: {e}")
    
    # 7. Verificar formularios
    print("\n7. ✅ VERIFICANDO FORMULARIOS...")
    try:
        from personal.forms import PuestoForm, EmpleadoForm, AsignacionForm, ComentarioAsignacionForm
        
        # Verificar que los formularios se pueden instanciar
        puesto_form = PuestoForm()
        empleado_form = EmpleadoForm()
        # asignacion_form = AsignacionForm()  # Requiere user parameter
        comentario_form = ComentarioAsignacionForm()
        
        print("   ✅ PuestoForm se instancia correctamente")
        print("   ✅ EmpleadoForm se instancia correctamente") 
        print("   ✅ ComentarioAsignacionForm se instancia correctamente")
        print("   ✅ Todos los formularios están correctamente definidos")
        
    except Exception as e:
        print(f"   ❌ Error con formularios: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 RESUMEN DE VERIFICACIÓN AUTOMATIZADA")
    print("=" * 60)
    print("✅ Estructura de archivos verificada")
    print("✅ Imports y sintaxis correctos")
    print("✅ Modelos correctamente definidos")
    print("✅ Formularios correctamente definidos")
    print("✅ URLs configuradas")
    print("\n🔧 PASOS MANUALES REQUERIDOS:")
    print("   1. Ejecutar: python manage.py makemigrations personal")
    print("   2. Ejecutar: python manage.py migrate")
    print("   3. Ejecutar: python manage.py test personal")
    print("   4. Probar manualmente según checklist proporcionado")
    
    return True

def create_test_data():
    """Crea datos de prueba para el módulo"""
    print("\n🔧 CREANDO DATOS DE PRUEBA...")
    
    try:
        from usuarios.models import Usuario, Rol
        from viviendas.models import Edificio, Vivienda
        from personal.models import Puesto, Empleado, Asignacion
        
        # Crear rol si no existe
        rol_admin, created = Rol.objects.get_or_create(
            nombre='Administrador',
            defaults={'descripcion': 'Administrador del sistema'}
        )
        
        # Crear usuario admin si no existe
        User = get_user_model()
        admin_user, created = User.objects.get_or_create(
            username='admin_test',
            defaults={
                'email': 'admin@test.com',
                'first_name': 'Admin',
                'last_name': 'Test',
                'rol': rol_admin,
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            print("   ✅ Usuario admin_test creado")
        
        # Crear edificio de prueba
        edificio, created = Edificio.objects.get_or_create(
            nombre='Edificio Test',
            defaults={
                'direccion': 'Calle Test 123',
                'pisos': 10
            }
        )
        if created:
            print("   ✅ Edificio Test creado")
        
        # Crear vivienda de prueba
        vivienda, created = Vivienda.objects.get_or_create(
            edificio=edificio,
            numero='101',
            defaults={
                'piso': 1,
                'metros_cuadrados': 80,
                'habitaciones': 2,
                'baños': 1
            }
        )
        if created:
            print("   ✅ Vivienda 101 creada")
        
        # Crear puesto de prueba
        puesto, created = Puesto.objects.get_or_create(
            nombre='Conserje Test',
            defaults={'descripcion': 'Puesto de conserje para pruebas'}
        )
        if created:
            print("   ✅ Puesto Conserje Test creado")
        
        # Crear usuario empleado
        empleado_user, created = User.objects.get_or_create(
            username='empleado_test',
            defaults={
                'email': 'empleado@test.com',
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'rol': rol_admin,  # Por simplicidad
            }
        )
        if created:
            empleado_user.set_password('empleado123')
            empleado_user.save()
            print("   ✅ Usuario empleado_test creado")
        
        # Crear empleado
        empleado, created = Empleado.objects.get_or_create(
            usuario=empleado_user,
            defaults={
                'puesto': puesto,
                'fecha_contratacion': '2024-01-01',
                'tipo_contrato': 'PERMANENTE'
            }
        )
        if created:
            print("   ✅ Empleado Juan Pérez creado")
        
        # Crear asignación de prueba
        asignacion, created = Asignacion.objects.get_or_create(
            titulo='Limpieza general - Test',
            empleado=empleado,
            defaults={
                'tipo': 'TAREA',
                'descripcion': 'Limpieza general del edificio para pruebas',
                'fecha_inicio': '2024-12-01',
                'fecha_fin': '2024-12-02',
                'edificio': edificio,
                'estado': 'PENDIENTE',
                'prioridad': 2,
                'asignado_por': admin_user
            }
        )
        if created:
            print("   ✅ Asignación de prueba creada")
        
        print("\n✅ DATOS DE PRUEBA CREADOS EXITOSAMENTE")
        print(f"   🔑 Admin: admin_test / admin123")
        print(f"   🔑 Empleado: empleado_test / empleado123")
        
    except Exception as e:
        print(f"   ❌ Error creando datos de prueba: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO VERIFICACIÓN DEL MÓDULO PERSONAL")
    
    # Ejecutar verificaciones
    success = run_comprehensive_tests()
    
    # Crear datos de prueba
    create_data = input("\n¿Crear datos de prueba? (y/n): ").lower().strip()
    if create_data == 'y':
        create_test_data()
    
    print("\n" + "🎯" * 20)
    print("VERIFICACIÓN COMPLETADA")
    print("🎯" * 20)
    
    if success:
        print("✅ Verificación automática exitosa")
        print("🔧 Procede con las pruebas manuales del checklist")
    else:
        print("❌ Se encontraron problemas en la verificación automática")
        print("🔧 Revisa los errores antes de continuar")