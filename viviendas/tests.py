from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from usuarios.models import Rol
from viviendas.models import Edificio, Vivienda, Residente

class ViviendaFilterTest(TestCase):
    """
    Pruebas para verificar el correcto funcionamiento de los filtros
    en el listado de viviendas.
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
        
        # Crear edificios de prueba
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
        
        # Crear viviendas de prueba en diferentes estados
        # Edificio 1
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
            edificio=self.edificio1,
            numero='201',
            piso=2,
            metros_cuadrados=90,
            habitaciones=3,
            baños=2,
            estado='DESOCUPADO',
            activo=True
        )
        
        self.vivienda3 = Vivienda.objects.create(
            edificio=self.edificio1,
            numero='301',
            piso=3,
            metros_cuadrados=85,
            habitaciones=2,
            baños=1,
            estado='MANTENIMIENTO',
            activo=True
        )
        
        # Edificio 2
        self.vivienda4 = Vivienda.objects.create(
            edificio=self.edificio2,
            numero='101',
            piso=1,
            metros_cuadrados=75,
            habitaciones=2,
            baños=1,
            estado='OCUPADO',
            activo=True
        )
        
        self.vivienda5 = Vivienda.objects.create(
            edificio=self.edificio2,
            numero='201',
            piso=2,
            metros_cuadrados=80,
            habitaciones=2,
            baños=1,
            estado='BAJA',
            activo=False
        )
        
        # Iniciar sesión
        self.client.login(username='admin', password='adminpassword')
    
    def test_filtro_edificio(self):
        """Test para verificar el filtro por edificio"""
        url = reverse('vivienda-list') + f'?edificio={self.edificio1.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['viviendas']), 3)  # 3 viviendas en Edificio 1
        
        # Verificar que solo se muestran viviendas del edificio 1
        for vivienda in response.context['viviendas']:
            self.assertEqual(vivienda.edificio.id, self.edificio1.id)
    
    def test_filtro_piso(self):
        """Test para verificar el filtro por piso"""
        url = reverse('vivienda-list') + '?piso=1'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Solo las viviendas del piso 1 (una en cada edificio)
        self.assertEqual(len(response.context['viviendas']), 2)
        
        # Verificar que solo se muestran viviendas del piso 1
        for vivienda in response.context['viviendas']:
            self.assertEqual(vivienda.piso, 1)
    
    def test_filtro_estado(self):
        """Test para verificar el filtro por estado"""
        url = reverse('vivienda-list') + '?estado=OCUPADO'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Solo las viviendas en estado OCUPADO (una en cada edificio)
        self.assertEqual(len(response.context['viviendas']), 2)
        
        # Verificar que solo se muestran viviendas en estado OCUPADO
        for vivienda in response.context['viviendas']:
            self.assertEqual(vivienda.estado, 'OCUPADO')
    
    def test_filtro_activo(self):
        """Test para verificar el filtro por activo/inactivo"""
        # Filtrar por inactivas
        url = reverse('vivienda-list') + '?activo=false'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Solo hay una vivienda inactiva
        self.assertEqual(len(response.context['viviendas']), 1)
        
        # Verificar que solo se muestran viviendas inactivas
        for vivienda in response.context['viviendas']:
            self.assertFalse(vivienda.activo)
    
    def test_multiples_filtros(self):
        """Test para verificar la aplicación de múltiples filtros simultáneamente"""
        url = reverse('vivienda-list') + f'?edificio={self.edificio1.id}&estado=DESOCUPADO'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Solo hay una vivienda en Edificio 1 con estado DESOCUPADO
        self.assertEqual(len(response.context['viviendas']), 1)
        self.assertEqual(response.context['viviendas'][0].edificio.id, self.edificio1.id)
        self.assertEqual(response.context['viviendas'][0].estado, 'DESOCUPADO')

class ResidenteFilterTest(TestCase):
    """
    Pruebas para verificar el correcto funcionamiento de los filtros
    en el listado de residentes.
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
        
        # Crear edificios de prueba
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
        
        # Crear viviendas de prueba
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
        
        # Crear usuarios para residentes
        self.usuario1 = User.objects.create_user(
            username='residente1',
            email='residente1@example.com',
            password='password1',
            first_name='Juan',
            last_name='Pérez',
            rol=None
        )
        
        self.usuario2 = User.objects.create_user(
            username='residente2',
            email='residente2@example.com',
            password='password2',
            first_name='Ana',
            last_name='Gómez',
            rol=None
        )
        
        self.usuario3 = User.objects.create_user(
            username='residente3',
            email='residente3@example.com',
            password='password3',
            first_name='Carlos',
            last_name='López',
            rol=None
        )
        
        self.usuario4 = User.objects.create_user(
            username='residente4',
            email='residente4@example.com',
            password='password4',
            first_name='María',
            last_name='Rodríguez',
            rol=None,
            is_active=False
        )
        
        # Crear residentes
        self.residente1 = Residente.objects.create(
            usuario=self.usuario1,
            vivienda=self.vivienda1,
            vehiculos=1,
            es_propietario=True,
            activo=True
        )
        
        self.residente2 = Residente.objects.create(
            usuario=self.usuario2,
            vivienda=self.vivienda1,
            vehiculos=0,
            es_propietario=False,
            activo=True
        )
        
        self.residente3 = Residente.objects.create(
            usuario=self.usuario3,
            vivienda=self.vivienda2,
            vehiculos=2,
            es_propietario=True,
            activo=True
        )
        
        self.residente4 = Residente.objects.create(
            usuario=self.usuario4,
            vivienda=self.vivienda2,
            vehiculos=1,
            es_propietario=False,
            activo=False
        )
        
        # Iniciar sesión
        self.client.login(username='admin', password='adminpassword')
    
    def test_filtro_edificio(self):
        """Test para verificar el filtro por edificio"""
        url = reverse('residente-list') + f'?edificio={self.edificio1.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['residentes']), 2)  # 2 residentes en Edificio 1
        
        # Verificar que solo se muestran residentes del edificio 1
        for residente in response.context['residentes']:
            self.assertEqual(residente.vivienda.edificio.id, self.edificio1.id)
    
    def test_filtro_vivienda(self):
        """Test para verificar el filtro por vivienda"""
        url = reverse('residente-list') + f'?vivienda={self.vivienda2.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Hay 2 residentes en la vivienda 2, pero uno está inactivo
        self.assertEqual(len(response.context['residentes']), 2)
        
        # Verificar que solo se muestran residentes de la vivienda 2
        for residente in response.context['residentes']:
            self.assertEqual(residente.vivienda.id, self.vivienda2.id)
    
    def test_filtro_es_propietario(self):
        """Test para verificar el filtro por propietario"""
        url = reverse('residente-list') + '?es_propietario=true'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Hay 2 propietarios
        self.assertEqual(len(response.context['residentes']), 2)
        
        # Verificar que solo se muestran propietarios
        for residente in response.context['residentes']:
            self.assertTrue(residente.es_propietario)
    
    def test_filtro_estado(self):
        """Test para verificar el filtro por estado (activo/inactivo)"""
        url = reverse('residente-list') + '?estado=inactivo'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Hay 1 residente inactivo
        self.assertEqual(len(response.context['residentes']), 1)
        
        # Verificar que solo se muestran residentes inactivos
        for residente in response.context['residentes']:
            self.assertFalse(residente.activo)
    
    def test_multiples_filtros(self):
        """Test para verificar la aplicación de múltiples filtros simultáneamente"""
        url = reverse('residente-list') + f'?edificio={self.edificio1.id}&es_propietario=true'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Solo hay un propietario en el Edificio 1
        self.assertEqual(len(response.context['residentes']), 1)
        self.assertEqual(response.context['residentes'][0].vivienda.edificio.id, self.edificio1.id)
        self.assertTrue(response.context['residentes'][0].es_propietario)