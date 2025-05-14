from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Visita, MovimientoResidente
from usuarios.models import Rol
from viviendas.models import Edificio, Vivienda, Residente
from datetime import timedelta

class VisitaModelTest(TestCase):
    """
    Pruebas para el modelo Visita
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
        
        # Crear edificio, vivienda y residente
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
        
        self.usuario_residente = User.objects.create_user(
            username='residente',
            email='residente@example.com',
            password='password',
            first_name='Juan',
            last_name='Pérez'
        )
        
        self.residente = Residente.objects.create(
            usuario=self.usuario_residente,
            vivienda=self.vivienda,
            es_propietario=True
        )
        
        # Crear visita
        self.fecha_entrada = timezone.now()
        self.visita = Visita.objects.create(
            nombre_visitante='Ana Gómez',
            documento_visitante='12345678',
            vivienda_destino=self.vivienda,
            residente_autoriza=self.residente,
            fecha_hora_entrada=self.fecha_entrada,
            motivo='Visita familiar',
            registrado_por=self.admin_user
        )
    
    def test_visita_creation(self):
        """Verificar la creación correcta de una visita"""
        self.assertEqual(self.visita.nombre_visitante, 'Ana Gómez')
        self.assertEqual(self.visita.documento_visitante, '12345678')
        self.assertEqual(self.visita.vivienda_destino, self.vivienda)
        self.assertEqual(self.visita.residente_autoriza, self.residente)
        self.assertEqual(self.visita.fecha_hora_entrada, self.fecha_entrada)
        self.assertIsNone(self.visita.fecha_hora_salida)
        self.assertEqual(self.visita.motivo, 'Visita familiar')
        self.assertEqual(self.visita.registrado_por, self.admin_user)
    
    def test_visita_str(self):
        """Verificar que el método __str__ funciona correctamente"""
        expected_str = f"Ana Gómez - {self.vivienda} - {self.fecha_entrada.strftime('%d/%m/%Y %H:%M')}"
        self.assertEqual(str(self.visita), expected_str)

class MovimientoResidenteModelTest(TestCase):
    """
    Pruebas para el modelo MovimientoResidente
    """
    
    def setUp(self):
        # Crear edificio, vivienda y residente
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
        
        User = get_user_model()
        self.usuario_residente = User.objects.create_user(
            username='residente',
            email='residente@example.com',
            password='password',
            first_name='Juan',
            last_name='Pérez'
        )
        
        self.residente = Residente.objects.create(
            usuario=self.usuario_residente,
            vivienda=self.vivienda,
            es_propietario=True
        )
        
        # Crear movimientos
        self.fecha_entrada = timezone.now()
        self.fecha_salida = self.fecha_entrada + timedelta(hours=2)
        
        # Movimiento de entrada
        self.movimiento_entrada = MovimientoResidente.objects.create(
            residente=self.residente,
            fecha_hora_entrada=self.fecha_entrada,
            fecha_hora_salida=None,
            vehiculo=True,
            placa_vehiculo='ABC123'
        )
        
        # Movimiento de salida
        self.movimiento_salida = MovimientoResidente.objects.create(
            residente=self.residente,
            fecha_hora_entrada=None,
            fecha_hora_salida=self.fecha_salida,
            vehiculo=False,
            placa_vehiculo=''
        )
    
    def test_movimiento_entrada_creation(self):
        """Verificar la creación correcta de un movimiento de entrada"""
        self.assertEqual(self.movimiento_entrada.residente, self.residente)
        self.assertEqual(self.movimiento_entrada.fecha_hora_entrada, self.fecha_entrada)
        self.assertIsNone(self.movimiento_entrada.fecha_hora_salida)
        self.assertTrue(self.movimiento_entrada.vehiculo)
        self.assertEqual(self.movimiento_entrada.placa_vehiculo, 'ABC123')
    
    def test_movimiento_salida_creation(self):
        """Verificar la creación correcta de un movimiento de salida"""
        self.assertEqual(self.movimiento_salida.residente, self.residente)
        self.assertIsNone(self.movimiento_salida.fecha_hora_entrada)
        self.assertEqual(self.movimiento_salida.fecha_hora_salida, self.fecha_salida)
        self.assertFalse(self.movimiento_salida.vehiculo)
        self.assertEqual(self.movimiento_salida.placa_vehiculo, '')
    
    def test_movimiento_str(self):
        """Verificar que el método __str__ funciona correctamente"""
        # Para movimiento de entrada
        expected_str_entrada = f"{self.residente} - Entrada - {self.fecha_entrada.strftime('%d/%m/%Y %H:%M')}"
        self.assertEqual(str(self.movimiento_entrada), expected_str_entrada)
        
        # Para movimiento de salida
        expected_str_salida = f"{self.residente} - Salida - {self.fecha_salida.strftime('%d/%m/%Y %H:%M')}"
        self.assertEqual(str(self.movimiento_salida), expected_str_salida)

class VisitaViewsTest(TestCase):
    """
    Pruebas para las vistas relacionadas con Visitas
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
        
        # Crear edificio, vivienda y residente
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
        
        self.usuario_residente = User.objects.create_user(
            username='residente',
            email='residente@example.com',
            password='password',
            first_name='Juan',
            last_name='Pérez'
        )
        
        self.residente = Residente.objects.create(
            usuario=self.usuario_residente,
            vivienda=self.vivienda,
            es_propietario=True
        )
        
        # Crear visitas
        self.fecha_entrada = timezone.now()
        self.visita_activa = Visita.objects.create(
            nombre_visitante='Ana Gómez',
            documento_visitante='12345678',
            vivienda_destino=self.vivienda,
            residente_autoriza=self.residente,
            fecha_hora_entrada=self.fecha_entrada,
            motivo='Visita familiar',
            registrado_por=self.admin_user
        )
        
        self.visita_completa = Visita.objects.create(
            nombre_visitante='Carlos Ruiz',
            documento_visitante='87654321',
            vivienda_destino=self.vivienda,
            residente_autoriza=self.residente,
            fecha_hora_entrada=self.fecha_entrada - timedelta(hours=3),
            fecha_hora_salida=self.fecha_entrada - timedelta(hours=1),
            motivo='Entrega de paquete',
            registrado_por=self.admin_user
        )
        
        # Iniciar sesión
        self.client.login(username='admin', password='adminpassword')
    
    def test_visita_list_view(self):
        """Verificar que la vista de lista de visitas funciona correctamente"""
        response = self.client.get(reverse('visita-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accesos/visita_list.html')
        
        # Verificar que solo muestra visitas activas
        self.assertEqual(len(response.context['visitas']), 1)
        self.assertEqual(response.context['visitas'][0], self.visita_activa)
        
        # Verificar que cuenta correctamente las visitas históricas
        self.assertEqual(response.context['visitas_historicas'], 1)
    
    def test_visita_create_view(self):
        """Verificar que la vista de creación de visitas funciona correctamente"""
        response = self.client.get(reverse('visita-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accesos/visita_form.html')
    
    def test_registrar_salida_visita(self):
        """Verificar que el registro de salida funciona correctamente"""
        response = self.client.get(reverse('visita-salida', args=[self.visita_activa.id]))
        self.assertRedirects(response, reverse('visita-list'))
        
        # Verificar que se registró la salida
        self.visita_activa.refresh_from_db()
        self.assertIsNotNone(self.visita_activa.fecha_hora_salida)

class MovimientoResidenteViewsTest(TestCase):
    """
    Pruebas para las vistas relacionadas con Movimientos de Residentes
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
        
        # Crear edificio, vivienda y residente
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
        
        self.usuario_residente = User.objects.create_user(
            username='residente',
            email='residente@example.com',
            password='password',
            first_name='Juan',
            last_name='Pérez'
        )
        
        self.residente = Residente.objects.create(
            usuario=self.usuario_residente,
            vivienda=self.vivienda,
            es_propietario=True
        )
        
        # Crear movimiento
        self.fecha = timezone.now()
        self.movimiento = MovimientoResidente.objects.create(
            residente=self.residente,
            fecha_hora_entrada=self.fecha,
            vehiculo=True,
            placa_vehiculo='ABC123'
        )
        
        # Iniciar sesión
        self.client.login(username='admin', password='adminpassword')
    
    def test_movimiento_list_view(self):
        """Verificar que la vista de lista de movimientos funciona correctamente"""
        response = self.client.get(reverse('movimiento-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accesos/movimiento_list.html')
        
        # Verificar que muestra el movimiento creado
        self.assertEqual(len(response.context['movimientos']), 1)
    
    def test_movimiento_entrada_view(self):
        """Verificar que la vista de registro de entrada funciona correctamente"""
        response = self.client.get(reverse('movimiento-entrada'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accesos/movimiento_entrada_form.html')
        
        # Probar el POST
        data = {
            'residente': self.residente.id,
            'vehiculo': False,
            'placa_vehiculo': ''
        }
        
        response = self.client.post(reverse('movimiento-entrada'), data)
        self.assertRedirects(response, reverse('movimiento-list'))
        
        # Verificar que se creó un nuevo movimiento
        self.assertEqual(MovimientoResidente.objects.count(), 2)
        nuevo_movimiento = MovimientoResidente.objects.latest('id')
        self.assertEqual(nuevo_movimiento.residente, self.residente)
        self.assertIsNotNone(nuevo_movimiento.fecha_hora_entrada)
        self.assertIsNone(nuevo_movimiento.fecha_hora_salida)
    
    def test_movimiento_salida_view(self):
        """Verificar que la vista de registro de salida funciona correctamente"""
        response = self.client.get(reverse('movimiento-salida'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accesos/movimiento_salida_form.html')
        
        # Probar el POST
        data = {
            'residente': self.residente.id,
            'vehiculo': True,
            'placa_vehiculo': 'XYZ789'
        }
        
        response = self.client.post(reverse('movimiento-salida'), data)
        self.assertRedirects(response, reverse('movimiento-list'))
        
        # Verificar que se creó un nuevo movimiento
        self.assertEqual(MovimientoResidente.objects.count(), 2)
        nuevo_movimiento = MovimientoResidente.objects.latest('id')
        self.assertEqual(nuevo_movimiento.residente, self.residente)
        self.assertIsNone(nuevo_movimiento.fecha_hora_entrada)
        self.assertIsNotNone(nuevo_movimiento.fecha_hora_salida)
        self.assertTrue(nuevo_movimiento.vehiculo)
        self.assertEqual(nuevo_movimiento.placa_vehiculo, 'XYZ789')