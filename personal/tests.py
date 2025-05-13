from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from usuarios.models import Rol
from .models import Puesto, Empleado, Asignacion
from viviendas.models import Edificio, Vivienda

class EmpleadoFilterTest(TestCase):
    """
    Pruebas para verificar el correcto funcionamiento de los filtros
    en el listado de empleados.
    """
    
    def setUp(self):
        # Crear usuario de prueba con rol administrador
        self.rol_admin = Rol.objects.create(nombre='Administrador', descripcion='Administrador del sistema')
        
        User = get_user_model()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            rol=self.rol_admin
        )
        
        # Crear puestos de prueba
        self.puesto1 = Puesto.objects.create(
            nombre='Conserje',
            descripcion='Encargado de la limpieza',
            requiere_especializacion=False
        )
        
        self.puesto2 = Puesto.objects.create(
            nombre='Técnico de Mantenimiento',
            descripcion='Reparaciones y mantenimiento',
            requiere_especializacion=True
        )
        
        # Crear usuarios para empleados
        self.usuario1 = User.objects.create_user(
            username='empleado1',
            email='empleado1@example.com',
            password='password1',
            first_name='Pedro',
            last_name='Martínez',
            rol=None
        )
        
        self.usuario2 = User.objects.create_user(
            username='empleado2',
            email='empleado2@example.com',
            password='password2',
            first_name='Lucía',
            last_name='García',
            rol=None
        )
        
        self.usuario3 = User.objects.create_user(
            username='empleado3',
            email='empleado3@example.com',
            password='password3',
            first_name='Roberto',
            last_name='Fernández',
            rol=None
        )
        
        self.usuario4 = User.objects.create_user(
            username='empleado4',
            email='empleado4@example.com',
            password='password4',
            first_name='Sofía',
            last_name='Torres',
            rol=None,
            is_active=False
        )
        
        # Crear empleados
        self.empleado1 = Empleado.objects.create(
            usuario=self.usuario1,
            puesto=self.puesto1,
            fecha_contratacion='2020-01-15',
            tipo_contrato='PERMANENTE',
            activo=True
        )
        
        self.empleado2 = Empleado.objects.create(
            usuario=self.usuario2,
            puesto=self.puesto1,
            fecha_contratacion='2021-03-20',
            tipo_contrato='TEMPORAL',
            activo=True
        )
        
        self.empleado3 = Empleado.objects.create(
            usuario=self.usuario3,
            puesto=self.puesto2,
            fecha_contratacion='2019-11-10',
            tipo_contrato='PERMANENTE',
            activo=True
        )
        
        self.empleado4 = Empleado.objects.create(
            usuario=self.usuario4,
            puesto=self.puesto2,
            fecha_contratacion='2022-05-05',
            tipo_contrato='EXTERNO',
            activo=False
        )
        
        # Iniciar sesión
        self.client.login(username='admin', password='adminpassword')
    
    def test_filtro_puesto(self):
        """Test para verificar el filtro por puesto"""
        url = reverse('empleado-list') + f'?puesto={self.puesto1.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['empleados']), 2)  # 2 empleados con puesto1
        
        # Verificar que solo se muestran empleados del puesto1
        for empleado in response.context['empleados']:
            self.assertEqual(empleado.puesto.id, self.puesto1.id)
    
    def test_filtro_estado(self):
        """Test para verificar el filtro por estado (activo/inactivo)"""
        url = reverse('empleado-list') + '?estado=inactivo'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Hay 1 empleado inactivo
        self.assertEqual(len(response.context['empleados']), 1)
        
        # Verificar que solo se muestran empleados inactivos
        for empleado in response.context['empleados']:
            self.assertFalse(empleado.activo)
    
    def test_filtro_busqueda_texto(self):
        """Test para verificar el filtro por búsqueda de texto"""
        # Buscar por nombre
        url = reverse('empleado-list') + '?q=Pedro'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['empleados']), 1)
        self.assertEqual(response.context['empleados'][0].usuario.first_name, 'Pedro')
        
        # Buscar por apellido
        url = reverse('empleado-list') + '?q=García'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['empleados']), 1)
        self.assertEqual(response.context['empleados'][0].usuario.last_name, 'García')
        
        # Buscar por puesto
        url = reverse('empleado-list') + '?q=Conserje'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['empleados']), 2)
        for empleado in response.context['empleados']:
            self.assertEqual(empleado.puesto.nombre, 'Conserje')
    
    def test_multiples_filtros(self):
        """Test para verificar la aplicación de múltiples filtros simultáneamente"""
        url = reverse('empleado-list') + f'?puesto={self.puesto1.id}&estado=activo'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Hay 2 empleados activos con puesto1
        self.assertEqual(len(response.context['empleados']), 2)
        
        for empleado in response.context['empleados']:
            self.assertEqual(empleado.puesto.id, self.puesto1.id)
            self.assertTrue(empleado.activo)

class AsignacionFilterTest(TestCase):
    """
    Pruebas para verificar el correcto funcionamiento de los filtros
    en el listado de asignaciones.
    """
    
    def setUp(self):
        # Crear usuario de prueba con rol administrador
        self.rol_admin = Rol.objects.create(nombre='Administrador', descripcion='Administrador del sistema')
        
        User = get_user_model()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            rol=self.rol_admin
        )
        
        # Crear puestos
        self.puesto = Puesto.objects.create(
            nombre='Mantenimiento',
            descripcion='Reparaciones y mantenimiento',
            requiere_especializacion=True
        )
        
        # Crear usuarios para empleados
        self.usuario1 = User.objects.create_user(
            username='empleado1',
            email='empleado1@example.com',
            password='password1',
            first_name='Pedro',
            last_name='Martínez',
            rol=None
        )
        
        self.usuario2 = User.objects.create_user(
            username='empleado2',
            email='empleado2@example.com',
            password='password2',
            first_name='Lucía',
            last_name='García',
            rol=None
        )
        
        # Crear empleados
        self.empleado1 = Empleado.objects.create(
            usuario=self.usuario1,
            puesto=self.puesto,
            fecha_contratacion='2020-01-15',
            tipo_contrato='PERMANENTE',
            activo=True
        )
        
        self.empleado2 = Empleado.objects.create(
            usuario=self.usuario2,
            puesto=self.puesto,
            fecha_contratacion='2021-03-20',
            tipo_contrato='TEMPORAL',
            activo=True
        )
        
        # Crear edificios
        self.edificio1 = Edificio.objects.create(
            nombre='Edificio A',
            direccion='Calle Principal 123',
            pisos=10,
            fecha_construccion='2015-01-01'
        )
        
        self.edificio2 = Edificio.objects.create(
            nombre='Edificio B',
            direccion='Avenida Central 456',
            pisos=5,
            fecha_construccion='2018-06-15'
        )
        
        # Crear viviendas
        self.vivienda1 = Vivienda.objects.create(
            edificio=self.edificio1,
            numero='101',
            piso=1,
            metros_cuadrados=80,
            habitaciones=2,
            baños=1,
            estado='OCUPADO',
            activo=True
        )
        
        self.vivienda2 = Vivienda.objects.create(
            edificio=self.edificio2,
            numero='101',
            piso=1,
            metros_cuadrados=75,
            habitaciones=2,
            baños=1,
            estado='OCUPADO',
            activo=True
        )
        
        # Crear asignaciones
        fecha_hoy = timezone.now().date()
        
        self.asignacion1 = Asignacion.objects.create(
            empleado=self.empleado1,
            tipo='TAREA',
            titulo='Reparación de goteras',
            descripcion='Reparar goteras en el techo',
            fecha_inicio=fecha_hoy,
            edificio=self.edificio1,
            vivienda=self.vivienda1,
            estado='PENDIENTE',
            prioridad=2,
            asignado_por=self.admin_user
        )
        
        self.asignacion2 = Asignacion.objects.create(
            empleado=self.empleado1,
            tipo='RESPONSABILIDAD',
            titulo='Mantenimiento mensual',
            descripcion='Revisión general de instalaciones',
            fecha_inicio=fecha_hoy,
            edificio=self.edificio1,
            estado='EN_PROGRESO',
            prioridad=1,
            asignado_por=self.admin_user
        )
        
        self.asignacion3 = Asignacion.objects.create(
            empleado=self.empleado2,
            tipo='TAREA',
            titulo='Reparación aire acondicionado',
            descripcion='Revisar y reparar aire acondicionado',
            fecha_inicio=fecha_hoy - timezone.timedelta(days=5),
            fecha_fin=fecha_hoy + timezone.timedelta(days=2),
            edificio=self.edificio2,
            vivienda=self.vivienda2,
            estado='COMPLETADA',
            prioridad=3,
            asignado_por=self.admin_user
        )
        
        # Iniciar sesión
        self.client.login(username='admin', password='adminpassword')
    
    def test_filtro_empleado(self):
        """Test para verificar el filtro por empleado"""
        url = reverse('asignacion-list') + f'?empleado={self.empleado1.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['asignaciones']), 2)  # 2 asignaciones para empleado1
        
        # Verificar que solo se muestran asignaciones del empleado1
        for asignacion in response.context['asignaciones']:
            self.assertEqual(asignacion.empleado.id, self.empleado1.id)
    
    def test_filtro_tipo(self):
        """Test para verificar el filtro por tipo de asignación"""
        url = reverse('asignacion-list') + '?tipo=TAREA'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['asignaciones']), 2)  # 2 asignaciones de tipo TAREA
        
        # Verificar que solo se muestran asignaciones de tipo TAREA
        for asignacion in response.context['asignaciones']:
            self.assertEqual(asignacion.tipo, 'TAREA')
    
    def test_filtro_estado(self):
        """Test para verificar el filtro por estado de asignación"""
        url = reverse('asignacion-list') + '?estado=COMPLETADA'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['asignaciones']), 1)  # 1 asignación completada
        
        # Verificar que solo se muestran asignaciones en estado COMPLETADA
        for asignacion in response.context['asignaciones']:
            self.assertEqual(asignacion.estado, 'COMPLETADA')
    
    def test_filtro_edificio(self):
        """Test para verificar el filtro por edificio"""
        url = reverse('asignacion-list') + f'?edificio={self.edificio1.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['asignaciones']), 2)  # 2 asignaciones en edificio1
        
        # Verificar que solo se muestran asignaciones del edificio1
        for asignacion in response.context['asignaciones']:
            self.assertEqual(asignacion.edificio.id, self.edificio1.id)
    
    def test_filtro_fecha(self):
        """Test para verificar el filtro por fecha"""
        fecha_hoy = timezone.now().date()
        fecha_desde = (fecha_hoy - timezone.timedelta(days=3)).strftime('%Y-%m-%d')
        
        url = reverse('asignacion-list') + f'?fecha_desde={fecha_desde}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Deberían mostrarse las asignaciones con fecha_inicio >= fecha_desde
        self.assertEqual(len(response.context['asignaciones']), 2)
    
    def test_multiples_filtros(self):
        """Test para verificar la aplicación de múltiples filtros simultáneamente"""
        url = reverse('asignacion-list') + f'?empleado={self.empleado1.id}&tipo=TAREA'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Solo hay 1 asignación de tipo TAREA para empleado1
        self.assertEqual(len(response.context['asignaciones']), 1)
        
        asignacion = response.context['asignaciones'][0]
        self.assertEqual(asignacion.empleado.id, self.empleado1.id)
        self.assertEqual(asignacion.tipo, 'TAREA')