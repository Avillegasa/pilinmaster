from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Rol, Usuario

class RolModelTest(TestCase):
    """
    Pruebas para el modelo Rol
    """
    
    def setUp(self):
        self.rol = Rol.objects.create(
            nombre='Test Rol',
            descripcion='Rol para pruebas'
        )
    
    def test_rol_creation(self):
        """Verificar la creación correcta de un rol"""
        self.assertEqual(self.rol.nombre, 'Test Rol')
        self.assertEqual(self.rol.descripcion, 'Rol para pruebas')
    
    def test_rol_str(self):
        """Verificar que el método __str__ funciona correctamente"""
        self.assertEqual(str(self.rol), 'Test Rol')

class UsuarioModelTest(TestCase):
    """
    Pruebas para el modelo Usuario
    """
    
    def setUp(self):
        self.rol = Rol.objects.create(
            nombre='Test Rol',
            descripcion='Rol para pruebas'
        )
        
        User = get_user_model()
        self.usuario = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User',
            rol=self.rol,
            telefono='1234567890',
            tipo_documento='DNI',
            numero_documento='12345678'
        )
    
    def test_usuario_creation(self):
        """Verificar la creación correcta de un usuario"""
        self.assertEqual(self.usuario.username, 'testuser')
        self.assertEqual(self.usuario.email, 'test@example.com')
        self.assertEqual(self.usuario.first_name, 'Test')
        self.assertEqual(self.usuario.last_name, 'User')
        self.assertEqual(self.usuario.rol, self.rol)
        self.assertEqual(self.usuario.telefono, '1234567890')
        self.assertEqual(self.usuario.tipo_documento, 'DNI')
        self.assertEqual(self.usuario.numero_documento, '12345678')
    
    def test_usuario_str(self):
        """Verificar que el método __str__ funciona correctamente"""
        self.assertEqual(str(self.usuario), 'Test User - testuser')

class UsuarioViewTest(TestCase):
    """
    Pruebas para las vistas de Usuario
    """
    
    def setUp(self):
        # Crear un rol administrador
        self.rol_admin = Rol.objects.create(
            nombre='Administrador',
            descripcion='Administrador del sistema'
        )
        
        # Crear un rol no administrador
        self.rol_normal = Rol.objects.create(
            nombre='Normal',
            descripcion='Usuario normal'
        )
        
        # Crear usuario administrador
        User = get_user_model()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            first_name='Admin',
            last_name='User',
            rol=self.rol_admin
        )
        
        # Crear usuario normal
        self.normal_user = User.objects.create_user(
            username='normal',
            email='normal@example.com',
            password='normalpassword',
            first_name='Normal',
            last_name='User',
            rol=self.rol_normal
        )
    
    def test_list_view_admin_access(self):
        """Verificar que un administrador puede acceder a la lista de usuarios"""
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('usuario-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/usuario_list.html')
    
    def test_list_view_normal_access_denied(self):
        """Verificar que un usuario normal no puede acceder a la lista de usuarios"""
        self.client.login(username='normal', password='normalpassword')
        response = self.client.get(reverse('usuario-list'))
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_change_state_view(self):
        """Verificar el funcionamiento correcto de la vista de cambio de estado"""
        self.client.login(username='admin', password='adminpassword')
        
        # Verificar GET
        response = self.client.get(reverse('usuario-change-state', args=[self.normal_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/usuario_change_state.html')
        
        # Verificar POST (desactivar usuario)
        response = self.client.post(reverse('usuario-change-state', args=[self.normal_user.id]))
        self.normal_user.refresh_from_db()
        self.assertFalse(self.normal_user.is_active)
        
        # Verificar POST (activar usuario)
        response = self.client.post(reverse('usuario-change-state', args=[self.normal_user.id]))
        self.normal_user.refresh_from_db()
        self.assertTrue(self.normal_user.is_active)
    
    def test_cannot_change_own_state(self):
        """Verificar que un administrador no puede cambiar su propio estado"""
        self.client.login(username='admin', password='adminpassword')
        
        response = self.client.post(reverse('usuario-change-state', args=[self.admin_user.id]))
        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.is_active)  # Sigue activo