#!/usr/bin/env python
"""
Script para verificar la integridad de los datos después de las correcciones
Ejecutar desde el directorio del proyecto: python check_integrity.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'condominio_app.settings')
django.setup()

from django.db import connection
from usuarios.models import Usuario, Rol
from viviendas.models import Edificio, Vivienda, Residente
from financiero.models import ConceptoCuota, Cuota, Pago
from personal.models import Empleado, Puesto

def verificar_integridad():
    print("🔍 VERIFICANDO INTEGRIDAD DEL SISTEMA")
    print("=" * 50)
    
    errores = []
    advertencias = []
    
    # ✅ 1. Verificar roles básicos
    print("\n1. Verificando roles básicos...")
    roles_requeridos = ['Administrador', 'Gerente', 'Residente', 'Personal', 'Vigilante']
    for rol_nombre in roles_requeridos:
        try:
            rol = Rol.objects.get(nombre=rol_nombre)
            print(f"   ✅ Rol '{rol_nombre}' existe")
        except Rol.DoesNotExist:
            errores.append(f"❌ Rol '{rol_nombre}' no existe")
    
    # ✅ 2. Verificar usuarios sin rol
    print("\n2. Verificando usuarios sin rol...")
    usuarios_sin_rol = Usuario.objects.filter(rol__isnull=True)
    if usuarios_sin_rol.exists():
        advertencias.append(f"⚠️  {usuarios_sin_rol.count()} usuarios sin rol asignado")
        for usuario in usuarios_sin_rol:
            print(f"   - {usuario.username}")
    else:
        print("   ✅ Todos los usuarios tienen rol asignado")
    
    # ✅ 3. Verificar residentes sin vivienda
    print("\n3. Verificando residentes sin vivienda...")
    residentes_sin_vivienda = Residente.objects.filter(vivienda__isnull=True)
    if residentes_sin_vivienda.exists():
        errores.append(f"❌ {residentes_sin_vivienda.count()} residentes sin vivienda")
        for residente in residentes_sin_vivienda:
            print(f"   - {residente.usuario.username}")
    else:
        print("   ✅ Todos los residentes tienen vivienda asignada")
    
    # ✅ 4. Verificar empleados con rol Personal
    print("\n4. Verificando empleados con rol Personal...")
    empleados = Empleado.objects.all()
    empleados_sin_rol_personal = 0
    for empleado in empleados:
        if not empleado.usuario.rol or empleado.usuario.rol.nombre != 'Personal':
            empleados_sin_rol_personal += 1
            print(f"   ⚠️  {empleado.usuario.username} no tiene rol 'Personal'")
    
    if empleados_sin_rol_personal == 0:
        print(f"   ✅ Todos los {empleados.count()} empleados tienen rol 'Personal'")
    else:
        advertencias.append(f"⚠️  {empleados_sin_rol_personal} empleados sin rol 'Personal'")
    
    # ✅ 5. Verificar viviendas con estado inconsistente
    print("\n5. Verificando estados de vivienda...")
    viviendas_ocupadas = Vivienda.objects.filter(estado='OCUPADO')
    viviendas_sin_residentes = []
    
    for vivienda in viviendas_ocupadas:
        residentes_activos = vivienda.residentes.filter(activo=True).count()
        if residentes_activos == 0:
            viviendas_sin_residentes.append(vivienda)
    
    if viviendas_sin_residentes:
        advertencias.append(f"⚠️  {len(viviendas_sin_residentes)} viviendas marcadas como 'OCUPADO' sin residentes activos")
        for vivienda in viviendas_sin_residentes[:5]:  # Mostrar solo las primeras 5
            print(f"   - {vivienda.edificio.nombre} - {vivienda.numero}")
    else:
        print("   ✅ Estados de vivienda consistentes")
    
    # ✅ 6. Verificar cuotas sin concepto
    print("\n6. Verificando cuotas...")
    cuotas_sin_concepto = Cuota.objects.filter(concepto__isnull=True)
    if cuotas_sin_concepto.exists():
        errores.append(f"❌ {cuotas_sin_concepto.count()} cuotas sin concepto")
    else:
        print("   ✅ Todas las cuotas tienen concepto asignado")
    
    # ✅ 7. Verificar pagos sin vivienda
    print("\n7. Verificando pagos...")
    pagos_sin_vivienda = Pago.objects.filter(vivienda__isnull=True)
    if pagos_sin_vivienda.exists():
        errores.append(f"❌ {pagos_sin_vivienda.count()} pagos sin vivienda")
    else:
        print("   ✅ Todos los pagos tienen vivienda asignada")
    
    # ✅ 8. Verificar gerentes sin edificio
    print("\n8. Verificando gerentes...")
    usuarios_gerentes = Usuario.objects.filter(rol__nombre='Gerente')
    gerentes_sin_edificio = []
    for usuario in usuarios_gerentes:
        if not hasattr(usuario, 'gerente'):
            gerentes_sin_edificio.append(usuario)
    
    if gerentes_sin_edificio:
        errores.append(f"❌ {len(gerentes_sin_edificio)} usuarios con rol Gerente sin edificio asignado")
        for gerente in gerentes_sin_edificio:
            print(f"   - {gerente.username}")
    else:
        print(f"   ✅ Todos los {usuarios_gerentes.count()} gerentes tienen edificio asignado")
    
    # ✅ 9. Verificar conexión a base de datos
    print("\n9. Verificando conexión a base de datos...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("   ✅ Conexión a base de datos exitosa")
    except Exception as e:
        errores.append(f"❌ Error de conexión a BD: {e}")
    
    # ✅ 10. Estadísticas generales
    print("\n10. Estadísticas generales...")
    print(f"   📊 Usuarios totales: {Usuario.objects.count()}")
    print(f"   📊 Edificios: {Edificio.objects.count()}")
    print(f"   📊 Viviendas activas: {Vivienda.objects.filter(activo=True).count()}")
    print(f"   📊 Residentes activos: {Residente.objects.filter(activo=True).count()}")
    print(f"   📊 Empleados activos: {Empleado.objects.filter(activo=True).count()}")
    print(f"   📊 Cuotas totales: {Cuota.objects.count()}")
    print(f"   📊 Pagos verificados: {Pago.objects.filter(estado='VERIFICADO').count()}")
    
    # ✅ RESUMEN FINAL
    print("\n" + "=" * 50)
    print("📋 RESUMEN DE VERIFICACIÓN")
    print("=" * 50)
    
    if not errores and not advertencias:
        print("🎉 ¡PERFECTO! No se encontraron errores ni advertencias")
        print("   El sistema está íntegro y listo para usar")
    else:
        if errores:
            print(f"❌ ERRORES CRÍTICOS ({len(errores)}):")
            for error in errores:
                print(f"   {error}")
            print("\n⚡ Estos errores deben corregirse antes de usar el sistema")
        
        if advertencias:
            print(f"\n⚠️  ADVERTENCIAS ({len(advertencias)}):")
            for advertencia in advertencias:
                print(f"   {advertencia}")
            print("\n💡 Estas advertencias pueden corregirse opcionalmente")
    
    print("\n🔧 Para corregir problemas automáticamente, ejecuta:")
    print("   python manage.py shell")
    print("   >>> exec(open('fix_data_integrity.py').read())")
    
    return len(errores) == 0

def generar_script_correccion():
    """Genera un script para corregir los problemas encontrados"""
    script_content = '''
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
'''
    
    with open('fix_data_integrity.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"\n📝 Script de corrección generado: fix_data_integrity.py")

if __name__ == "__main__":
    try:
        integridad_ok = verificar_integridad()
        generar_script_correccion()
        
        if integridad_ok:
            sys.exit(0)  # Éxito
        else:
            sys.exit(1)  # Errores encontrados
            
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)  # Error de ejecución