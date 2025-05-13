from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Visita, MovimientoResidente
from usuarios.models import Rol
from viviendas.models import Edificio, Vivienda, Residente

class VisitaFilterTest(TestCase):
    """
    Pruebas para verificar el correcto funcionamiento del historial de visitas.
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
        
        # Crear edificios
        self.edificio = Edificio.objects.create(
            nombre='Edificio A',
            direccion='Calle Principal 123',
            pisos=10,
            fecha_construccion='2015-01-01'
        )
        
        # Crear vivienda
        self.vivienda = Vivienda.objects.create(
            edificio=self.edificio,
            numero='101',
            piso=1,
            metros_cuadrados=80,
            habitaciones=2,
            baños=1,
            estado='OCUPADO',
            activo=True
        )
        
        # Crear usuario para residente
        self.usuario_residente = User.objects.create_user(
            username='residente',
            email='residente@example.com',
            password='password',
            first_name='Juan',
            last_name='Pérez',
            rol=None
        )
        
        # Crear residente
        self.residente = Residente.objects.create(
            usuario=self.usuario_residente,
            vivienda=self.vivienda,
            vehiculos=1,
            es_propietario=True,
            activo=True
        )
        
        # Crear visitas
        fecha_hora = timezone.now()
        
        # Visita activa
        self.visita1 = Visita.objects.create(
            nombre_visitante='Ana Gómez',
            documento_visitante='12345678',
            vivienda_destino=self.vivienda,
            residente_autoriza=self.residente,
            fecha_hora_entrada=fecha_hora - timezone.timedelta(hours=2),
            fecha_hora_salida=None,
            motivo='Visita familiar',
            registrado_por=self.admin_user
        )
        
        # Visita completada (con salida)
        self.visita2 = Visita.objects.create(
            nombre_visitante='Carlos López',
            documento_visitante='87654321',
            vivienda_destino=self.vivienda,
            residente_autoriza=self.residente,
            fecha_hora_entrada=fecha_hora - timezone.timedelta(days=1, hours=3),
            fecha_hora_salida=fecha_hora - timezone.timedelta(days=1, hours=1),
            motivo='Entrega de paquete',
            registrado_por=self.admin_user
        )
        
        # Iniciar sesión
        self.client.login(username='admin', password='adminpassword')
    
    def test_lista_visitas_activas(self):
        """Test para verificar que solo se muestran las visitas activas por defecto"""
        url = reverse('visita-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Solo 1 visita activa (sin fecha de salida)
        self.assertEqual(response.context['visitas'].count(), 1)
        self.assertIsNone(response.context['visitas'].first().fecha_hora_salida)
    
    def test_contador_visitas_historicas(self):
        """Test para verificar que el contador de visitas históricas es correcto"""
        url = reverse('visita-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # 1 visita en el historial (con fecha de salida)
        self.assertEqual(response.context['visitas_historicas'], 1)

class MovimientoResidenteTest(TestCase):
    """
    Pruebas para verificar el correcto funcionamiento de los movimientos
    de entrada y salida de residentes.
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
        
        # Crear edificios
        self.edificio = Edificio.objects.create(
            nombre='Edificio A',
            direccion='Calle Principal 123',
            pisos=10,
            fecha_construccion='2015-01-01'
        )
        
        # Crear vivienda
        self.vivienda = Vivienda.objects.create(
            edificio=self.edificio,
            numero='101',
            piso=1,
            metros_cuadrados=80,
            habitaciones=2,
            baños=1,
            estado='OCUPADO',
            activo=True
        )
        
        # Crear usuarios para residentes
        self.usuario_residente1 = User.objects.create_user(
            username='residente1',
            email='residente1@example.com',
            password='password1',
            first_name='Juan',
            last_name='Pérez',
            rol=None
        )
        
        self.usuario_residente2 = User.objects.create_user(
            username='residente2',
            email='residente2@example.com',
            password='password2',
            first_name='Ana',
            last_name='Gómez',
            rol=None
        )
        
        # Crear residentes
        self.residente1 = Residente.objects.create(
            usuario=self.usuario_residente1,
            vivienda=self.vivienda,
            vehiculos=1,
            es_propietario=True,
            activo=True
        )
        
        self.residente2 = Residente.objects.create(
            usuario=self.usuario_residente2,
            vivienda=self.vivienda,
            vehiculos=0,
            es_propietario=False,
            activo=True
        )
        
        # Crear movimientos
        fecha_hora = timezone.now()
        
        # Entrada de residente1 con vehículo
        self.movimiento1 = MovimientoResidente.objects.create(
            residente=self.residente1,
            fecha_hora_entrada=fecha_hora - timezone.timedelta(hours=2),
            fecha_hora_salida=None,
            vehiculo=True,
            placa_vehiculo='ABC123'
        )
        
        # Salida de residente2 sin vehículo
        self.movimiento2 = MovimientoResidente.objects.create(
            residente=self.residente2,
            fecha_hora_entrada=None,
            fecha_hora_salida=fecha_hora - timezone.timedelta(hours=1),
            vehiculo=False,
            placa_vehiculo=''
        )
        
        # Iniciar sesión
        self.client.login(username='admin', password='adminpassword')
    
    def test_lista_movimientos(self):
        """Test para verificar que se muestran todos los movimientos"""
        url = reverse('movimiento-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # 2 movimientos en total
        self.assertEqual(response.context['movimientos'].count(), 2)
    
    def test_formulario_entrada(self):
        """Test para verificar que el formulario de entrada muestra solo residentes activos"""
        url = reverse('movimiento-entrada')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Verificar que el formulario solo muestra residentes activos
        form = response.context['form']
        self.assertEqual(form.fields['residente'].queryset.count(), 2)
        
        # Desactivar un residente
        self.residente2.activo = False
        self.residente2.save()
        
        # Verificar que ahora solo muestra un residente
        response = self.client.get(url)
        form = response.context['form']
        self.assertEqual(form.fields['residente'].queryset.count(), 1)
    
    def test_registro_entrada(self):
        """Test para verificar que se puede registrar una entrada correctamente"""
        url = reverse('movimiento-entrada')
        data = {
            'residente': self.residente2.id,
            'vehiculo': False,
            'placa_vehiculo': ''
        }
        
        response = self.client.post(url, data, follow=True)
        
        self.assertEqual(response.status_code, 200)
        # Verificar que se creó un nuevo movimiento
        self.assertEqual(MovimientoResidente.objects.count(), 3)
        
        # Verificar que el nuevo movimiento es de entrada
        nuevo_movimiento = MovimientoResidente.objects.latest('id')
        self.assertIsNotNone(nuevo_movimiento.fecha_hora_entrada)
        self.assertIsNone(nuevo_movimiento.fecha_hora_salida)
        self.assertEqual(nuevo_movimiento.residente.id, self.residente2.id)
    
    def test_registro_salida(self):
        """Test para verificar que se puede registrar una salida correctamente"""
        url = reverse('movimiento-salida')
        data = {
            'residente': self.residente1.id,
            'vehiculo': True,
            'placa_vehiculo': 'ABC123'
        }
        
        response = self.client.post(url, data, follow=True)
        
        self.assertEqual(response.status_code, 200)
        # Verificar que se creó un nuevo movimiento
        self.assertEqual(MovimientoResidente.objects.count(), 3)
        
        # Verificar que el nuevo movimiento es de salida
        nuevo_movimiento = MovimientoResidente.objects.latest('id')
        self.assertIsNone(nuevo_movimiento.fecha_hora_entrada)
        self.assertIsNotNone(nuevo_movimiento.fecha_hora_salida)
        self.assertEqual(nuevo_movimiento.residente.id, self.residente1.id)
        self.assertTrue(nuevo_movimiento.vehiculo)
        self.assertEqual(nuevo_movimiento.placa_vehiculo, 'ABC123')