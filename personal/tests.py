from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, date
from usuarios.models import Rol
from viviendas.models import Edificio, Vivienda
from .models import Puesto, Empleado, Asignacion, ComentarioAsignacion

class PuestoModelTest(TestCase):
    """
    Pruebas para el modelo Puesto
    """
    
    def setUp(self):
        self.puesto = Puesto.objects.create(
            nombre='Conserje',
            descripcion='Encargado de la limpieza y vigilancia',
            requiere_especializacion=False
        )
    
    def test_puesto_creation(self):
        """Verificar la creación correcta de un puesto"""
        self.assertEqual(self.puesto.nombre, 'Conserje')
        self.assertEqual(self.puesto.descripcion, 'Encargado de la limpieza y vigilancia')
        self.assertFalse(self.puesto.requiere_especializacion)
    
    def test_puesto_str(self):
        """Verificar que el método __str__ funciona correctamente"""
        self.assertEqual(str(self.puesto), 'Conserje')

class EmpleadoModelTest(TestCase):
    """
    Pruebas para el modelo Empleado
    """
    
    def setUp(self):
        # Crear puesto
        self.puesto = Puesto.objects.create(
            nombre='Mantenimiento',
            descripcion='Encargado del mantenimiento',
            requiere_especializacion=True
        )
        
        # Crear usuario
        User = get_user_model()
        self.usuario = User.objects.create_user(
            username='empleado',
            email='empleado@example.com',
            password='password',
            first_name='Pedro',
            last_name='García'
        )
        
        # Crear empleado
        self.fecha_contratacion = date(2020, 1, 15)
        self.empleado = Empleado.objects.create(
            usuario=self.usuario,
            puesto=self.puesto,
            fecha_contratacion=self.fecha_contratacion,
            tipo_contrato='PERMANENTE',
            salario=1500.00,
            contacto_emergencia='María García',
            telefono_emergencia='9876543210',
            especialidad='Electricidad',
            activo=True
        )
    
    def test_empleado_creation(self):
        """Verificar la creación correcta de un empleado"""
        self.assertEqual(self.empleado.usuario, self.usuario)
        self.assertEqual(self.empleado.puesto, self.puesto)
        self.assertEqual(self.empleado.fecha_contratacion, self.fecha_contratacion)
        self.assertEqual(self.empleado.tipo_contrato, 'PERMANENTE')
        self.assertEqual(self.empleado.salario, 1500.00)
        self.assertEqual(self.empleado.contacto_emergencia, 'María García')
        self.assertEqual(self.empleado.telefono_emergencia, '9876543210')
        self.assertEqual(self.empleado.especialidad, 'Electricidad')
        self.assertTrue(self.empleado.activo)
    
    def test_empleado_str(self):
        """Verificar que el método __str__ funciona correctamente"""
        expected_str = f"Pedro García - Mantenimiento"
        self.assertEqual(str(self.empleado), expected_str)
    
    def test_sincronizacion_estado_usuario(self):
        """Verificar que el estado del empleado se sincroniza con el usuario"""
        # Desactivar usuario
        self.usuario.is_active = False
        self.usuario.save()
        
        # Verificar que el empleado también se desactiva
        self.empleado.refresh_from_db()
        self.assertFalse(self.empleado.activo)
        
        # Activar usuario
        self.usuario.is_active = True
        self.usuario.save()
        
        # Verificar que el empleado también se activa
        self.empleado.refresh_from_db()
        self.assertTrue(self.empleado.activo)

class AsignacionModelTest(TestCase):
    """
    Pruebas para el modelo Asignacion
    """
    
    def setUp(self):
        # Crear puesto y empleado
        self.puesto = Puesto.objects.create(
            nombre='Mantenimiento',
            descripcion='Encargado del mantenimiento',
            requiere_especializacion=True
        )
        
        User = get_user_model()
        self.usuario_empleado = User.objects.create_user(
            username='empleado',
            email='empleado@example.com',
            password='password',
            first_name='Pedro',
            last_name='García'
        )
        
        self.empleado = Empleado.objects.create(
            usuario=self.usuario_empleado,
            puesto=self.puesto,
            fecha_contratacion=date(2020, 1, 15),
            tipo_contrato='PERMANENTE',
            activo=True
        )
        
        # Crear edificio y vivienda
        self.edificio = Edificio.objects.create(
            nombre='Edificio Test',
            direccion='Calle Test 123',
            pisos=10
        )
        
        self.vivienda = Vivienda.objects.create(
            edificio=self.edificio,
            numero='101',
            piso=1,
            metros_cuadrados=80,
            habitaciones=2,
            baños=1
        )
        
        # Crear usuario administrador
        self.rol_admin = Rol.objects.create(nombre='Administrador', descripcion='Administrador del sistema')
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            rol=self.rol_admin
        )
        
        # Crear asignación
        self.fecha_asignacion = timezone.now().date()
        self.fecha_inicio = self.fecha_asignacion
        self.fecha_fin = self.fecha_asignacion + timedelta(days=5)
        
        self.asignacion = Asignacion.objects.create(
            empleado=self.empleado,
            tipo='TAREA',
            titulo='Reparación de goteras',
            descripcion='Revisar y reparar goteras en el baño',
            fecha_inicio=self.fecha_inicio,
            fecha_fin=self.fecha_fin,
            edificio=self.edificio,
            vivienda=self.vivienda,
            estado='PENDIENTE',
            prioridad=3,
            notas='Usar materiales impermeables',
            asignado_por=self.admin_user
        )
    
    def test_asignacion_creation(self):
        """Verificar la creación correcta de una asignación"""
        self.assertEqual(self.asignacion.empleado, self.empleado)
        self.assertEqual(self.asignacion.tipo, 'TAREA')
        self.assertEqual(self.asignacion.titulo, 'Reparación de goteras')
        self.assertEqual(self.asignacion.descripcion, 'Revisar y reparar goteras en el baño')
        self.assertEqual(self.asignacion.fecha_inicio, self.fecha_inicio)
        self.assertEqual(self.asignacion.fecha_fin, self.fecha_fin)
        self.assertEqual(self.asignacion.edificio, self.edificio)
        self.assertEqual(self.asignacion.vivienda, self.vivienda)
        self.assertEqual(self.asignacion.estado, 'PENDIENTE')
        self.assertEqual(self.asignacion.prioridad, 3)
        self.assertEqual(self.asignacion.notas, 'Usar materiales impermeables')
        self.assertEqual(self.asignacion.asignado_por, self.admin_user)
    
    def test_asignacion_str(self):
        """Verificar que el método __str__ funciona correctamente"""
        expected_str = f"Reparación de goteras - {self.empleado}"
        self.assertEqual(str(self.asignacion), expected_str)

class ComentarioAsignacionModelTest(TestCase):
    """
    Pruebas para el modelo ComentarioAsignacion
    """
    
    def setUp(self):
        # Crear puesto y empleado
        self.puesto = Puesto.objects.create(
            nombre='Mantenimiento',
            descripcion='Encargado del mantenimiento',
            requiere_especializacion=True
        )
        
        User = get_user_model()
        self.usuario_empleado = User.objects.create_user(
            username='empleado',
            email='empleado@example.com',
            password='password',
            first_name='Pedro',
            last_name='García'
        )
        
        self.empleado = Empleado.objects.create(
            usuario=self.usuario_empleado,
            puesto=self.puesto,
            fecha_contratacion=date(2020, 1, 15),
            tipo_contrato='PERMANENTE',
            activo=True
        )
        
        # Crear edificio
        self.edificio = Edificio.objects.create(
            nombre='Edificio Test',
            direccion='Calle Test 123',
            pisos=10
        )
        
        # Crear usuario administrador
        self.rol_admin = Rol.objects.create(nombre='Administrador', descripcion='Administrador del sistema')
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            rol=self.rol_admin
        )
        
        # Crear asignación
        self.asignacion = Asignacion.objects.create(
            empleado=self.empleado,
            tipo='TAREA',
            titulo='Revisión general',
            descripcion='Revisión de instalaciones',
            fecha_inicio=timezone.now().date(),
            edificio=self.edificio,
            estado='PENDIENTE',
            prioridad=2,
            asignado_por=self.admin_user
        )
        
        # Crear comentario
        self.fecha_comentario = timezone.now()
        self.comentario = ComentarioAsignacion.objects.create(
            asignacion=self.asignacion,
            usuario=self.admin_user,
            comentario='Se requiere terminar antes del viernes'
        )
    
    def test_comentario_creation(self):
        """Verificar la creación correcta de un comentario"""
        self.assertEqual(self.comentario.asignacion, self.asignacion)
        self.assertEqual(self.comentario.usuario, self.admin_user)
        self.assertEqual(self.comentario.comentario, 'Se requiere terminar antes del viernes')
        # Verificar que la fecha se asigna automáticamente
        self.assertIsNotNone(self.comentario.fecha)
    
    def test_comentario_str(self):
        """Verificar que el método __str__ funciona correctamente"""
        expected_str = f"Comentario de {self.admin_user} en {self.asignacion.titulo}"
        self.assertEqual(str(self.comentario), expected_str)

class PuestoViewsTest(TestCase):
    """
    Pruebas para las vistas relacionadas con Puestos
    """
    
    def setUp(self):
        # Crear usuario administrador
        self.rol_admin = Rol.objects.create(nombre='Administrador', descripcion='Administrador del sistema')
        
        User = get_user_model()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            rol=self.rol_admin
        )
        
        # Crear usuario normal
        self.rol_normal = Rol.objects.create(nombre='Normal', descripcion='Usuario normal')
        self.normal_user = User.objects.create_user(
            username='normal',
            email='normal@example.com',
            password='normalpassword',
            rol=self.rol_normal
        )
        
        # Crear puesto
        self.puesto = Puesto.objects.create(
            nombre='Seguridad',
            descripcion='Personal de seguridad',
            requiere_especializacion=True
        )
        
        # Iniciar cliente
        self.client = Client()
    
    def test_puesto_list_view_admin(self):
        """Verificar que un administrador puede ver la lista de puestos"""
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('puesto-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/puesto_list.html')
        self.assertContains(response, 'Seguridad')
    
    def test_puesto_list_view_normal_user(self):
        """Verificar que un usuario normal no puede ver la lista de puestos"""
        self.client.login(username='normal', password='normalpassword')
        response = self.client.get(reverse('puesto-list'))
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_puesto_create_view_admin(self):
        """Verificar que un administrador puede crear un puesto"""
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('puesto-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/puesto_form.html')
        
        # Probar POST
        data = {
            'nombre': 'Jardinero',
            'descripcion': 'Mantenimiento de jardines',
            'requiere_especializacion': False
        }
        
        response = self.client.post(reverse('puesto-create'), data)
        self.assertEqual(response.status_code, 302)  # Redirección
        
        # Verificar que se creó el puesto
        self.assertTrue(Puesto.objects.filter(nombre='Jardinero').exists())
    
    def test_puesto_update_view_admin(self):
        """Verificar que un administrador puede actualizar un puesto"""
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('puesto-update', args=[self.puesto.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/puesto_form.html')
        
        # Probar POST
        data = {
            'nombre': 'Seguridad Avanzada',
            'descripcion': 'Personal de seguridad con formación avanzada',
            'requiere_especializacion': True
        }
        
        response = self.client.post(reverse('puesto-update', args=[self.puesto.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirección
        
        # Verificar que se actualizó el puesto
        self.puesto.refresh_from_db()
        self.assertEqual(self.puesto.nombre, 'Seguridad Avanzada')
    
    def test_puesto_delete_view_admin(self):
        """Verificar que un administrador puede eliminar un puesto"""
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('puesto-delete', args=[self.puesto.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/puesto_confirm_delete.html')
        
        # Probar POST
        response = self.client.post(reverse('puesto-delete', args=[self.puesto.id]))
        self.assertEqual(response.status_code, 302)  # Redirección
        
        # Verificar que se eliminó el puesto
        self.assertFalse(Puesto.objects.filter(id=self.puesto.id).exists())

class EmpleadoViewsTest(TestCase):
    """
    Pruebas para las vistas relacionadas con Empleados
    """
    
    def setUp(self):
        # Crear usuario administrador
        self.rol_admin = Rol.objects.create(nombre='Administrador', descripcion='Administrador del sistema')
        
        User = get_user_model()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            rol=self.rol_admin
        )
        
        # Crear usuario normal
        self.rol_normal = Rol.objects.create(nombre='Normal', descripcion='Usuario normal')
        self.normal_user = User.objects.create_user(
            username='normal',
            email='normal@example.com',
            password='normalpassword',
            rol=self.rol_normal
        )
        
        # Crear usuario para empleado
        self.usuario_empleado = User.objects.create_user(
            username='empleado',
            email='empleado@example.com',
            password='password',
            first_name='Pedro',
            last_name='García'
        )
        
        # Crear puesto
        self.puesto = Puesto.objects.create(
            nombre='Mantenimiento',
            descripcion='Encargado del mantenimiento',
            requiere_especializacion=True
        )
        
        # Crear empleado
        self.empleado = Empleado.objects.create(
            usuario=self.usuario_empleado,
            puesto=self.puesto,
            fecha_contratacion=date(2020, 1, 15),
            tipo_contrato='PERMANENTE',
            activo=True
        )
        
        # Iniciar cliente
        self.client = Client()
    
    def test_empleado_list_view(self):
        """Verificar que se puede ver la lista de empleados"""
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('empleado-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/empleado_list.html')
        self.assertContains(response, 'Pedro García')
    
    def test_empleado_detail_view(self):
        """Verificar que se puede ver el detalle de un empleado"""
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('empleado-detail', args=[self.empleado.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/empleado_detail.html')
        self.assertContains(response, 'Pedro García')
        self.assertContains(response, 'Mantenimiento')
    
    def test_empleado_change_state(self):
        """Verificar que se puede cambiar el estado de un empleado"""
        self.client.login(username='admin', password='adminpassword')
        
        # Verificar GET
        response = self.client.get(reverse('empleado-change-state', args=[self.empleado.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/empleado_change_state.html')
        
        # Verificar POST (desactivar empleado)
        response = self.client.post(reverse('empleado-change-state', args=[self.empleado.id]))
        self.assertEqual(response.status_code, 302)  # Redirección
        
        # Verificar que se desactivó el empleado y su usuario asociado
        self.empleado.refresh_from_db()
        self.usuario_empleado.refresh_from_db()
        self.assertFalse(self.empleado.activo)
        self.assertFalse(self.usuario_empleado.is_active)
        
        # Verificar POST (activar empleado)
        response = self.client.post(reverse('empleado-change-state', args=[self.empleado.id]))
        self.assertEqual(response.status_code, 302)  # Redirección
        
        # Verificar que se activó el empleado y su usuario asociado
        self.empleado.refresh_from_db()
        self.usuario_empleado.refresh_from_db()
        self.assertTrue(self.empleado.activo)
        self.assertTrue(self.usuario_empleado.is_active)

class AsignacionViewsTest(TestCase):
    """
    Pruebas para las vistas relacionadas con Asignaciones
    """
    
    def setUp(self):
        # Crear usuario administrador
        self.rol_admin = Rol.objects.create(nombre='Administrador', descripcion='Administrador del sistema')
        
        User = get_user_model()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            rol=self.rol_admin
        )
        
        # Crear usuario para empleado
        self.usuario_empleado = User.objects.create_user(
            username='empleado',
            email='empleado@example.com',
            password='password',
            first_name='Pedro',
            last_name='García'
        )
        
        # Crear puesto
        self.puesto = Puesto.objects.create(
            nombre='Mantenimiento',
            descripcion='Encargado del mantenimiento',
            requiere_especializacion=True
        )
        
        # Crear empleado
        self.empleado = Empleado.objects.create(
            usuario=self.usuario_empleado,
            puesto=self.puesto,
            fecha_contratacion=date(2020, 1, 15),
            tipo_contrato='PERMANENTE',
            activo=True
        )
        
        # Crear edificio y vivienda
        self.edificio = Edificio.objects.create(
            nombre='Edificio Test',
            direccion='Calle Test 123',
            pisos=10
        )
        
        self.vivienda = Vivienda.objects.create(
            edificio=self.edificio,
            numero='101',
            piso=1,
            metros_cuadrados=80,
            habitaciones=2,
            baños=1
        )
        
        # Crear asignación
        self.asignacion = Asignacion.objects.create(
            empleado=self.empleado,
            tipo='TAREA',
            titulo='Revisión general',
            descripcion='Revisión de instalaciones',
            fecha_inicio=timezone.now().date(),
            edificio=self.edificio,
            vivienda=self.vivienda,
            estado='PENDIENTE',
            prioridad=2,
            asignado_por=self.admin_user
        )
        
        # Iniciar cliente
        self.client = Client()
        self.client.login(username='admin', password='adminpassword')
    
    def test_asignacion_list_view(self):
        """Verificar que se puede ver la lista de asignaciones"""
        response = self.client.get(reverse('asignacion-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/asignacion_list.html')
        self.assertContains(response, 'Revisión general')
    
    def test_asignacion_detail_view(self):
        """Verificar que se puede ver el detalle de una asignación"""
        response = self.client.get(reverse('asignacion-detail', args=[self.asignacion.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/asignacion_detail.html')
        self.assertContains(response, 'Revisión general')
        self.assertContains(response, 'Revisión de instalaciones')
    
    def test_asignacion_create_view(self):
        """Verificar que se puede crear una asignación"""
        response = self.client.get(reverse('asignacion-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/asignacion_form.html')
    
    def test_cambiar_estado_asignacion(self):
        """Verificar que se puede cambiar el estado de una asignación"""
        # Verificar GET
        response = self.client.get(reverse('cambiar-estado-asignacion', args=[self.asignacion.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'personal/cambiar_estado_asignacion.html')
        
        # Verificar POST
        data = {
            'estado': 'EN_PROGRESO'
        }
        
        response = self.client.post(reverse('cambiar-estado-asignacion', args=[self.asignacion.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirección
        
        # Verificar que se cambió el estado
        self.asignacion.refresh_from_db()
        self.assertEqual(self.asignacion.estado, 'EN_PROGRESO')
        
        # Verificar que se creó un comentario automático
        comentario = ComentarioAsignacion.objects.filter(asignacion=self.asignacion).first()
        self.assertIsNotNone(comentario)
        self.assertEqual(comentario.usuario, self.admin_user)
        self.assertIn("Estado cambiado", comentario.comentario)
    
    def test_agregar_comentario_asignacion(self):
        """Verificar que se puede agregar un comentario a una asignación"""
        data = {
            'comentario': 'Comentario de prueba'
        }
        
        response = self.client.post(reverse('asignacion-detail', args=[self.asignacion.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirección
        
        # Verificar que se creó el comentario
        comentario = ComentarioAsignacion.objects.filter(
            asignacion=self.asignacion,
            comentario='Comentario de prueba'
        ).first()
        
        self.assertIsNotNone(comentario)
        self.assertEqual(comentario.usuario, self.admin_user)