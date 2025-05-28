# usuarios/management/commands/fix_personal_role.py
from django.core.management.base import BaseCommand
from django.db import transaction
from usuarios.models import Rol, Usuario

class Command(BaseCommand):
    """
    Comando para corregir el rol "Mantenimiento" por "Personal"
    ✅ CORRECCIÓN ERROR 3: Cambiar "Mantenimiento" por "Personal"
    
    Uso: python manage.py fix_personal_role
    """
    help = 'Corrige el rol "Mantenimiento" por "Personal" y actualiza usuarios asociados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula los cambios sin aplicarlos realmente',
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la corrección sin confirmación',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS('🔧 CORRECCIÓN ERROR 3: Cambiar rol "Mantenimiento" por "Personal"')
        )
        self.stdout.write('')
        
        try:
            with transaction.atomic():
                # 1. Verificar si existe rol "Mantenimiento"
                try:
                    rol_mantenimiento = Rol.objects.get(nombre='Mantenimiento')
                    self.stdout.write(f'✅ Encontrado rol "Mantenimiento" (ID: {rol_mantenimiento.id})')
                    usuarios_afectados = Usuario.objects.filter(rol=rol_mantenimiento)
                    self.stdout.write(f'👥 Usuarios con rol "Mantenimiento": {usuarios_afectados.count()}')
                    
                    for usuario in usuarios_afectados:
                        self.stdout.write(f'   - {usuario.username} ({usuario.first_name} {usuario.last_name})')
                    
                except Rol.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING('⚠️ No se encontró rol "Mantenimiento"')
                    )
                    rol_mantenimiento = None
                
                # 2. Verificar si existe rol "Personal"
                try:
                    rol_personal = Rol.objects.get(nombre='Personal')
                    self.stdout.write(f'✅ Encontrado rol "Personal" (ID: {rol_personal.id})')
                except Rol.DoesNotExist:
                    # Crear rol "Personal" si no existe
                    if not dry_run:
                        rol_personal = Rol.objects.create(
                            nombre='Personal',
                            descripcion='Personal de mantenimiento, limpieza y servicios del condominio. Acceso a módulo de personal y asignaciones.'
                        )
                        self.stdout.write(
                            self.style.SUCCESS(f'✅ Rol "Personal" creado (ID: {rol_personal.id})')
                        )
                    else:
                        self.stdout.write('🔄 [DRY RUN] Se crearían el rol "Personal"')
                        rol_personal = None
                
                # 3. Realizar la corrección
                if rol_mantenimiento and rol_personal:
                    if not dry_run:
                        if not force:
                            confirmacion = input('\n¿Deseas continuar con la corrección? (s/N): ')
                            if confirmacion.lower() != 's':
                                self.stdout.write(
                                    self.style.WARNING('❌ Operación cancelada por el usuario')
                                )
                                return
                        
                        # Transferir usuarios de "Mantenimiento" a "Personal"
                        usuarios_actualizados = usuarios_afectados.update(rol=rol_personal)
                        
                        self.stdout.write('')
                        self.stdout.write(
                            self.style.SUCCESS(f'✅ {usuarios_actualizados} usuarios actualizados de "Mantenimiento" a "Personal"')
                        )
                        
                        # Eliminar rol "Mantenimiento" si no tiene usuarios
                        if not rol_mantenimiento.usuarios.exists():
                            nombre_eliminado = rol_mantenimiento.nombre
                            rol_mantenimiento.delete()
                            self.stdout.write(
                                self.style.SUCCESS(f'🗑️ Rol "{nombre_eliminado}" eliminado exitosamente')
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(f'⚠️ No se pudo eliminar rol "Mantenimiento" - aún tiene usuarios asignados')
                            )
                    
                    else:
                        self.stdout.write('')
                        self.stdout.write('🔄 [DRY RUN] Cambios que se aplicarían:')
                        self.stdout.write(f'   - Transferir {usuarios_afectados.count()} usuarios de "Mantenimiento" a "Personal"')
                        self.stdout.write(f'   - Eliminar rol "Mantenimiento"')
                
                elif rol_mantenimiento and not rol_personal:
                    # Solo renombrar el rol existente
                    if not dry_run:
                        if not force:
                            confirmacion = input(f'\n¿Renombrar rol "Mantenimiento" a "Personal"? (s/N): ')
                            if confirmacion.lower() != 's':
                                self.stdout.write(
                                    self.style.WARNING('❌ Operación cancelada por el usuario')
                                )
                                return
                        
                        # Renombrar y actualizar descripción
                        rol_mantenimiento.nombre = 'Personal'
                        rol_mantenimiento.descripcion = 'Personal de mantenimiento, limpieza y servicios del condominio. Acceso a módulo de personal y asignaciones.'
                        rol_mantenimiento.save()
                        
                        self.stdout.write('')
                        self.stdout.write(
                            self.style.SUCCESS('✅ Rol "Mantenimiento" renombrado a "Personal" exitosamente')
                        )
                    else:
                        self.stdout.write('')
                        self.stdout.write('🔄 [DRY RUN] Cambios que se aplicarían:')
                        self.stdout.write('   - Renombrar rol "Mantenimiento" a "Personal"')
                        self.stdout.write('   - Actualizar descripción del rol')
                
                else:
                    self.stdout.write('')
                    self.stdout.write(
                        self.style.SUCCESS('✅ No se requieren cambios - rol "Personal" ya existe correctamente')
                    )
                
                # 4. Verificar estado final
                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS('📊 ESTADO FINAL:'))
                
                roles_actuales = Rol.objects.all().order_by('nombre')
                for rol in roles_actuales:
                    usuarios_count = rol.usuarios.count()
                    self.stdout.write(f'   🏷️ {rol.nombre}: {usuarios_count} usuarios')
                
                # 5. Verificar usuarios sin rol
                usuarios_sin_rol = Usuario.objects.filter(rol__isnull=True)
                if usuarios_sin_rol.exists():
                    self.stdout.write('')
                    self.stdout.write(
                        self.style.WARNING(f'⚠️ {usuarios_sin_rol.count()} usuarios sin rol asignado:')
                    )
                    for usuario in usuarios_sin_rol:
                        self.stdout.write(f'   - {usuario.username} ({usuario.first_name} {usuario.last_name})')
                
                if dry_run:
                    self.stdout.write('')
                    self.stdout.write(
                        self.style.WARNING('🔄 [DRY RUN] No se aplicaron cambios reales')
                    )
                    self.stdout.write('Para aplicar los cambios ejecuta: python manage.py fix_personal_role')
                else:
                    self.stdout.write('')
                    self.stdout.write(
                        self.style.SUCCESS('🎉 CORRECCIÓN COMPLETADA EXITOSAMENTE')
                    )
                    self.stdout.write('El rol "Personal" está ahora configurado correctamente')
        
        except Exception as e:
            self.stdout.write('')
            self.stdout.write(
                self.style.ERROR(f'❌ ERROR durante la corrección: {str(e)}')
            )
            self.stdout.write('La operación ha sido revertida automáticamente')
            raise