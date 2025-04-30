# Sistema de Administración de Condominios

Sistema web desarrollado con Django para la administración de condominios verticales (edificios).

## Características

- 🔐 **Gestión de Usuarios y Roles**: Control de acceso basado en roles (Administrador, Vigilante, Residente, Gerente)
- 🏢 **Gestión de Viviendas**: Administración de edificios, departamentos y sus características
- 👨‍👩‍👧‍👦 **Gestión de Residentes**: Registro de propietarios e inquilinos
- 🚶‍♂️ **Control de Acceso**: Registro de entradas y salidas de residentes y visitantes
- 📊 **Reportes**: Generación de informes en varios formatos

## Requisitos

- Python 3.8 o superior
- Django 4.2 o superior
- Otras dependencias en `requirements.txt`

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/condominio_app.git
   cd condominio_app
   ```

2. Crear y activar entorno virtual:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Realizar migraciones:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Ejecutar script de configuración inicial:
   ```bash
   python scripts/setup.py
   ```

6. Iniciar el servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```

7. Acceder al sistema en http://127.0.0.1:8000/

## Usuarios por defecto

El script de configuración crea los siguientes usuarios:

| Usuario    | Contraseña    | Rol          |
|------------|---------------|--------------|
| admin      | admin123      | Administrador|
| vigilante  | vigilante123  | Vigilante    |
| carlos     | carlos123     | Residente    |
| maria      | maria123      | Residente    |
| jorge      | jorge123      | Residente    |

## Estructura del proyecto

```
condominio_app/
├── condominio_app/      # Configuración principal del proyecto
├── usuarios/            # Gestión de usuarios y roles
├── viviendas/           # Gestión de edificios, viviendas y residentes
├── accesos/             # Control de entradas y salidas
├── reportes/            # Generación de informes
├── static/              # Archivos estáticos (CSS, JS)
├── media/               # Archivos subidos por los usuarios
├── templates/           # Plantillas HTML
├── scripts/             # Scripts de utilidad
├── manage.py            # Script de gestión de Django
└── requirements.txt     # Dependencias del proyecto
```

## Módulos principales

### Usuarios
- Gestión de perfiles de usuario
- Control de roles y permisos
- Autenticación y autorización

### Viviendas
- Gestión de edificios
- Administración de viviendas/departamentos
- Registro de residentes (propietarios e inquilinos)

### Accesos
- Registro de entradas y salidas de residentes
- Control de visitas
- Registro de vehículos

### Reportes
- Generación de informes sobre:
  - Accesos al condominio
  - Listados de residentes
  - Estado de viviendas
  - Informes financieros (futuro)

## Personalización

Para personalizar el sistema a las necesidades específicas de un condominio:

1. Modificar los modelos en cada aplicación según sea necesario
2. Actualizar las plantillas HTML para cambiar la apariencia
3. Ajustar los permisos en las vistas para controlar el acceso
4. Crear migraciones y aplicarlas a la base de datos

## Contribución

Si deseas contribuir a este proyecto:

1. Haz un fork del repositorio
2. Crea una nueva rama (`git checkout -b feature/nueva-caracteristica`)
3. Haz commit de tus cambios (`git commit -m 'Agregar nueva característica'`)
4. Haz push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## Configuración de la Autenticación con Google

Para habilitar el inicio de sesión con Google en el sistema de administración de condominios, sigue estos pasos:

## 1. Instalar Dependencias

Primero, asegúrate de que todas las dependencias estén instaladas:

```bash
pip install -r requirements.txt
```

## 2. Crear un Proyecto en la Consola de Desarrolladores de Google

1. Ve a la [Consola de Google Cloud](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Ve a "APIs & Servicios" > "Credenciales"
4. Haz clic en "Crear credenciales" y selecciona "ID de cliente OAuth"
5. Configura la pantalla de consentimiento si se te solicita
6. Para el tipo de aplicación, selecciona "Aplicación web"
7. Pon un nombre descriptivo para tu aplicación
8. En "Orígenes de JavaScript autorizados", agrega:
   ```
   http://localhost:8000
   ```
9. En "URIs de redirección autorizadas", agrega:
   ```
   http://localhost:8000/accounts/google/login/callback/
   ```
10. Haz clic en "Crear"
11. Anota el "ID de cliente" y la "Clave secreta de cliente" que se te proporcionarán

## 3. Configurar Django Allauth

1. Ajusta las siguientes variables en `settings.py`:

```python
GOOGLE_CLIENT_ID = 'tu-client-id'  # Reemplaza con tu ID de cliente
GOOGLE_SECRET = 'tu-secret-key'    # Reemplaza con tu clave secreta
```

2. Aplica las migraciones para crear las tablas necesarias:

```bash
python manage.py migrate
```

3. Crea un sitio en el admin de Django:
   - Accede a http://localhost:8000/admin/
   - Ve a "Sitios" y edita el sitio existente o crea uno nuevo
   - Establece el "Nombre del dominio" como "localhost:8000"
   - Establece el "Nombre visible" como "Torre Segura"

4. Configura el proveedor de Google:
   - En el admin de Django, ve a "Social Accounts" > "Social applications"
   - Haz clic en "Añadir social application"
   - Selecciona "Google" como proveedor
   - Ingresa un nombre descriptivo (por ejemplo, "Google Login")
   - Ingresa el ID de cliente y la clave secreta que obtuviste de Google
   - Añade el sitio que creaste anteriormente al campo "Sitios disponibles"
   - Guarda los cambios

## 4. Ajustes Adicionales (Opcional)

Para personalizar aún más la experiencia de inicio de sesión con Google, puedes modificar las siguientes configuraciones en `settings.py`:

```python
# Configuración de redes sociales
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'VERIFIED_EMAIL': True,
        'EXCHANGE_TOKEN': True,
        'LOCALE_FUNC': lambda request: 'es_MX',
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'verified',
            'locale',
            'picture',
        ],
    }
}
```

## 5. Asociación de Cuentas

Cuando un usuario inicia sesión con su cuenta de Google por primera vez, puedes:

1. **Crear una nueva cuenta de usuario**: Django AllAuth creará automáticamente una cuenta de usuario con la información del perfil de Google.
2. **Asociar con una cuenta existente**: Si deseas permitir que los usuarios asocien sus cuentas existentes con Google, asegúrate de tener habilitada la siguiente configuración:

```python
ACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_ADAPTER = 'usuarios.adapters.CustomSocialAccountAdapter'  # Opcional para personalizar el proceso
```

## 6. Configuración para Producción

Cuando despliegues el sistema en producción, asegúrate de:

1. Actualizar los "Orígenes de JavaScript autorizados" y "URIs de redirección autorizadas" en la Consola de Google Cloud con la URL de tu sitio en producción.
2. Actualizar el objeto "Sitio" en el admin de Django con el dominio correcto.
3. Usar variables de entorno para el ID de cliente y la clave secreta en lugar de codificarlos directamente en `settings.py`.

```python
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_SECRET = os.environ.get('GOOGLE_SECRET')
```

## 7. Funcionamiento

Una vez configurado, los usuarios podrán:

1. Hacer clic en el botón "Iniciar sesión con Google" en la página de login
2. Serán redirigidos a la pantalla de autenticación de Google
3. Después de autenticarse, regresarán a la aplicación y serán redirigidos al dashboard o a la página de completar perfil para nuevos usuarios

## 8. Solución de Problemas

Si encuentras problemas durante la configuración, verifica:

- Que las URIs de redirección sean exactamente las mismas en la Consola de Google y en tu configuración de Django
- Que la API de Google People esté habilitada en tu proyecto de Google Cloud
- Los registros de Django para mensajes de error específicos
- La configuración de SITE_ID en settings.py coincide con el ID del sitio creado

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.