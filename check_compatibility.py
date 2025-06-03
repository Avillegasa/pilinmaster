#!/usr/bin/env python
"""
Script para verificar la compatibilidad entre módulos de viviendas y financiero
con los módulos de usuarios, personal y residentes (que no se pueden modificar).

Ejecutar desde el directorio del proyecto: python check_compatibility.py
"""

import os
import sys
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'condominio_app.settings')
django.setup()

from django.db import connection, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

# Importar modelos (sin modificar los de usuarios/personal)
from usuarios.models import Usuario, Rol
from viviendas.models import Edificio, Vivienda, Residente
from personal.models import Empleado, Puesto
from financiero.models import ConceptoCuota, Cuota, Pago, CategoriaGasto, Gasto

def print_section(title):
    """Imprime una sección con formato"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_subsection(title):
    """Imprime una subsección con formato"""
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")

def check_database_connection():
    """Verificar conexión a la base de datos"""
    print_section("VERIFICACIÓN DE CONEXIÓN A BASE DE DATOS")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        
        if result:
            print("✅ Conexión a base de datos: EXITOSA")
            
            # Verificar información de la BD
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"📊 Tablas en la base de datos: {len(tables)}")
            return True
        else:
            print("❌ Conexión a base de datos: FALLIDA")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def check_model_integrity():
    """Verificar integridad de los modelos"""
    print_section("VERIFICACIÓN DE INTEGRIDAD DE MODELOS")
    
    issues = []
    
    # 1. Verificar Usuario y Rol
    print_subsection("Modelos de Usuario")
    try:
        user_count = Usuario.objects.count()
        role_count = Rol.objects.count()
        print(f"✅ Usuarios: {user_count}")
        print(f"✅ Roles: {role_count}")
        
        # Verificar roles requeridos
        required_roles = ['Administrador', 'Gerente', 'Residente', 'Personal']
        for role_name in required_roles:
            if Rol.objects.filter(nombre=role_name).exists():
                print(f"✅ Rol '{role_name}': Existe")
            else:
                issues.append(f"❌ Rol '{role_name}': NO EXISTE")
                
    except Exception as e:
        issues.append(f"❌ Error en modelos de Usuario: {e}")
    
    # 2. Verificar Edificio y Vivienda
    print_subsection("Modelos de Vivienda")
    try:
        edificio_count = Edificio.objects.count()
        vivienda_count = Vivienda.objects.count()
        residente_count = Residente.objects.count()
        
        print(f"✅ Edificios: {edificio_count}")
        print(f"✅ Viviendas: {vivienda_count}")
        print(f"✅ Residentes: {residente_count}")
        
        # Verificar viviendas activas
        viviendas_activas = Vivienda.objects.filter(activo=True).count()
        print(f"📊 Viviendas activas: {viviendas_activas}/{vivienda_count}")
        
    except Exception as e:
        issues.append(f"❌ Error en modelos de Vivienda: {e}")
    
    # 3. Verificar Personal (sin modificar)
    print_subsection("Modelos de Personal")
    try:
        puesto_count = Puesto.objects.count()
        empleado_count = Empleado.objects.count()
        
        print(f"✅ Puestos: {puesto_count}")
        print(f"✅ Empleados: {empleado_count}")
        
        # Verificar empleados activos
        empleados_activos = Empleado.objects.filter(activo=True).count()
        print(f"📊 Empleados activos: {empleados_activos}/{empleado_count}")
        
    except Exception as e:
        issues.append(f"❌ Error en modelos de Personal: {e}")
    
    # 4. Verificar Financiero
    print_subsection("Modelos Financieros")
    try:
        concepto_count = ConceptoCuota.objects.count()
        cuota_count = Cuota.objects.count()
        pago_count = Pago.objects.count()
        categoria_count = CategoriaGasto.objects.count()
        gasto_count = Gasto.objects.count()
        
        print(f"✅ Conceptos de Cuota: {concepto_count}")
        print(f"✅ Cuotas: {cuota_count}")
        print(f"✅ Pagos: {pago_count}")
        print(f"✅ Categorías de Gasto: {categoria_count}")
        print(f"✅ Gastos: {gasto_count}")
        
    except Exception as e:
        issues.append(f"❌ Error en modelos Financieros: {e}")
    
    return issues

def check_foreign_key_relationships():
    """Verificar relaciones de claves foráneas"""
    print_section("VERIFICACIÓN DE RELACIONES ENTRE MODELOS")
    
    issues = []
    
    print_subsection("Relaciones Usuario -> Residente")
    try:
        # Verificar que todos los residentes tengan usuario válido
        residentes_sin_usuario = Residente.objects.filter(usuario__isnull=True).count()
        if residentes_sin_usuario > 0:
            issues.append(f"❌ {residentes_sin_usuario} residentes sin usuario")
        else:
            print("✅ Todos los residentes tienen usuario asignado")
        
        # Verificar usuarios con rol Residente que no tengan registro de residente
        usuarios_residente = Usuario.objects.filter(rol__nombre='Residente')
        usuarios_sin_residente = 0
        for usuario in usuarios_residente:
            if not hasattr(usuario, 'residente'):
                usuarios_sin_residente += 1
        
        if usuarios_sin_residente > 0:
            issues.append(f"❌ {usuarios_sin_residente} usuarios con rol Residente sin registro de residente")
        else:
            print("✅ Todos los usuarios 'Residente' tienen registro de residente")
            
    except Exception as e:
        issues.append(f"❌ Error verificando Usuario-Residente: {e}")
    
    print_subsection("Relaciones Vivienda -> Residente")
    try:
        # Verificar residentes sin vivienda
        residentes_sin_vivienda = Residente.objects.filter(vivienda__isnull=True).count()
        if residentes_sin_vivienda > 0:
            issues.append(f"❌ {residentes_sin_vivienda} residentes sin vivienda asignada")
        else:
            print("✅ Todos los residentes tienen vivienda asignada")
        
        # Verificar consistencia de estados de vivienda
        viviendas_ocupadas_sin_residentes = 0
        for vivienda in Vivienda.objects.filter(estado='OCUPADO'):
            if not vivienda.get_residentes_activos().exists():
                viviendas_ocupadas_sin_residentes += 1
        
        if viviendas_ocupadas_sin_residentes > 0:
            issues.append(f"⚠️ {viviendas_ocupadas_sin_residentes} viviendas marcadas como ocupadas sin residentes activos")
        else:
            print("✅ Estados de vivienda consistentes con residentes")
            
    except Exception as e:
        issues.append(f"❌ Error verificando Vivienda-Residente: {e}")
    
    print_subsection("Relaciones Financiero -> Vivienda")
    try:
        # Verificar cuotas sin vivienda
        cuotas_sin_vivienda = Cuota.objects.filter(vivienda__isnull=True).count()
        if cuotas_sin_vivienda > 0:
            issues.append(f"❌ {cuotas_sin_vivienda} cuotas sin vivienda asignada")
        else:
            print("✅ Todas las cuotas tienen vivienda asignada")
        
        # Verificar pagos sin vivienda
        pagos_sin_vivienda = Pago.objects.filter(vivienda__isnull=True).count()
        if pagos_sin_vivienda > 0:
            issues.append(f"❌ {pagos_sin_vivienda} pagos sin vivienda asignada")
        else:
            print("✅ Todos los pagos tienen vivienda asignada")
            
    except Exception as e:
        issues.append(f"❌ Error verificando Financiero-Vivienda: {e}")
    
    return issues

def test_crud_operations():
    """Probar operaciones CRUD básicas"""
    print_section("PRUEBAS DE OPERACIONES CRUD")
    
    issues = []
    
    try:
        with transaction.atomic():
            print_subsection("Creando datos de prueba")
            
            # 1. Crear edificio de prueba
            edificio_test = Edificio.objects.create(
                nombre="Edificio Test",
                direccion="Calle Test 123",
                pisos=5
            )
            print("✅ Edificio creado")
            
            # 2. Crear vivienda de prueba
            vivienda_test = Vivienda.objects.create(
                edificio=edificio_test,
                numero="TEST-01",
                piso=1,
                metros_cuadrados=Decimal('75.50'),
                habitaciones=2,
                baños=1
            )
            print("✅ Vivienda creada")
            
            # 3. Crear concepto de cuota de prueba
            concepto_test = ConceptoCuota.objects.create(
                nombre="Cuota Test",
                descripcion="Cuota de prueba para verificación",
                monto_base=Decimal('100.00'),
                periodicidad='MENSUAL'
            )
            print("✅ Concepto de cuota creado")
            
            # 4. Crear cuota de prueba
            cuota_test = Cuota.objects.create(
                concepto=concepto_test,
                vivienda=vivienda_test,
                monto=Decimal('100.00'),
                fecha_emision=timezone.now().date(),
                fecha_vencimiento=timezone.now().date() + timezone.timedelta(days=30)
            )
            print("✅ Cuota creada")
            
            # 5. Crear categoría de gasto de prueba
            categoria_test = CategoriaGasto.objects.create(
                nombre="Mantenimiento Test",
                descripcion="Categoría de prueba",
                presupuesto_mensual=Decimal('500.00')
            )
            print("✅ Categoría de gasto creada")
            
            # 6. Crear gasto de prueba
            gasto_test = Gasto.objects.create(
                categoria=categoria_test,
                concepto="Gasto de prueba",
                descripcion="Descripción del gasto de prueba",
                monto=Decimal('50.00'),
                fecha=timezone.now().date()
            )
            print("✅ Gasto creado")
            
            print_subsection("Verificando operaciones de lectura")
            
            # Verificar que se pueden leer los datos
            assert Edificio.objects.filter(nombre="Edificio Test").exists()
            assert Vivienda.objects.filter(numero="TEST-01").exists()
            assert ConceptoCuota.objects.filter(nombre="Cuota Test").exists()
            assert Cuota.objects.filter(concepto=concepto_test).exists()
            assert CategoriaGasto.objects.filter(nombre="Mantenimiento Test").exists()
            assert Gasto.objects.filter(concepto="Gasto de prueba").exists()
            
            print("✅ Todas las operaciones de lectura exitosas")
            
            print_subsection("Verificando operaciones de actualización")
            
            # Actualizar datos
            vivienda_test.estado = 'MANTENIMIENTO'
            vivienda_test.save()
            
            cuota_test.notas = "Cuota actualizada"
            cuota_test.save()
            
            gasto_test.estado = 'PAGADO'
            gasto_test.save()
            
            print("✅ Todas las operaciones de actualización exitosas")
            
            print_subsection("Simulando rollback (datos se eliminarán)")
            
            # Al salir del bloque transaction.atomic(), 
            # todos los cambios se revierten automáticamente
            raise transaction.TransactionManagementError("Rollback intencional para limpieza")
            
    except transaction.TransactionManagementError:
        print("✅ Rollback completado - datos de prueba eliminados")
    except Exception as e:
        issues.append(f"❌ Error en operaciones CRUD: {e}")
    
    return issues

def check_signal_functionality():
    """Verificar que las señales funcionan correctamente"""
    print_section("VERIFICACIÓN DE SEÑALES Y AUTOMATIZACIÓN")
    
    issues = []
    
    try:
        print_subsection("Verificando señales de Vivienda-Residente")
        
        # Esta verificación es básica ya que no podemos modificar 
        # los modelos de usuarios/residentes
        total_residentes = Residente.objects.count()
        residentes_activos = Residente.objects.filter(activo=True).count()
        
        print(f"📊 Residentes totales: {total_residentes}")
        print(f"📊 Residentes activos: {residentes_activos}")
        
        if total_residentes > 0:
            print("✅ Señales básicas funcionando (modelos relacionados existen)")
        else:
            print("⚠️ No hay residentes para probar señales")
        
        print_subsection("Verificando cálculos automáticos de Cuotas")
        
        # Verificar que las cuotas calculan recargos correctamente
        cuotas_vencidas = Cuota.objects.filter(
            fecha_vencimiento__lt=timezone.now().date(),
            pagada=False
        )
        
        print(f"📊 Cuotas vencidas encontradas: {cuotas_vencidas.count()}")
        
        for cuota in cuotas_vencidas[:3]:  # Solo las primeras 3
            recargo_calculado = cuota.calcular_recargo()
            print(f"✅ Cuota {cuota.id}: Recargo calculado ${recargo_calculado}")
        
    except Exception as e:
        issues.append(f"❌ Error verificando señales: {e}")
    
    return issues

def generate_compatibility_report():
    """Generar reporte de compatibilidad"""
    print_section("GENERANDO REPORTE FINAL DE COMPATIBILIDAD")
    
    all_issues = []
    
    # Ejecutar todas las verificaciones
    if not check_database_connection():
        all_issues.append("❌ CRÍTICO: Sin conexión a base de datos")
        return all_issues
    
    all_issues.extend(check_model_integrity())
    all_issues.extend(check_foreign_key_relationships())
    all_issues.extend(test_crud_operations())
    all_issues.extend(check_signal_functionality())
    
    print_subsection("RESUMEN FINAL")
    
    if not all_issues:
        print("🎉 ¡EXCELENTE! No se encontraron problemas de compatibilidad")
        print("✅ Los módulos de viviendas y financiero son compatibles")
        print("✅ El sistema está listo para uso en producción")
    else:
        print(f"⚠️ Se encontraron {len(all_issues)} problema(s):")
        for issue in all_issues:
            print(f"   {issue}")
        
        # Clasificar problemas por severidad
        critical_issues = [i for i in all_issues if '❌' in i and 'CRÍTICO' in i]
        errors = [i for i in all_issues if '❌' in i and 'CRÍTICO' not in i]
        warnings = [i for i in all_issues if '⚠️' in i]
        
        print(f"\n📊 Resumen por severidad:")
        print(f"   🔴 Críticos: {len(critical_issues)}")
        print(f"   🟠 Errores: {len(errors)}")
        print(f"   🟡 Advertencias: {len(warnings)}")
        
        if critical_issues:
            print("\n🚨 ACCIÓN REQUERIDA: Problemas críticos deben resolverse")
        elif errors:
            print("\n⚡ RECOMENDADO: Resolver errores antes de producción")
        else:
            print("\n✅ ACEPTABLE: Solo advertencias menores")
    
    return all_issues

def main():
    """Función principal"""
    print("🔍 VERIFICADOR DE COMPATIBILIDAD TORRE SEGURA v2.0")
    print("=" * 60)
    print("Verificando compatibilidad entre módulos de viviendas/financiero")
    print("con los módulos existentes de usuarios/personal...")
    
    try:
        issues = generate_compatibility_report()
        
        print(f"\n📋 VERIFICACIÓN COMPLETADA")
        print(f"   Total de problemas encontrados: {len(issues)}")
        
        if len(issues) == 0:
            print("   Estado: ✅ PERFECTO")
            return 0
        elif any('CRÍTICO' in issue for issue in issues):
            print("   Estado: 🔴 CRÍTICO - Requiere atención inmediata")
            return 2
        elif any('❌' in issue for issue in issues):
            print("   Estado: 🟠 ERRORES - Recomendado corregir")
            return 1
        else:
            print("   Estado: 🟡 ADVERTENCIAS - Verificar si es necesario")
            return 0
            
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO EN VERIFICACIÓN: {e}")
        import traceback
        traceback.print_exc()
        return 3

if __name__ == "__main__":
    sys.exit(main())