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

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.