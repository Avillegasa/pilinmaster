"""
Django settings for condominio_app project.
Sistema Torre Segura - Configuración optimizada para Railway
"""

import os
from pathlib import Path
from datetime import timedelta
import environ
import socket

# ===========================
# CONFIGURACIÓN BASE
# ===========================

hostname = socket.gethostname()
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment variables
env = environ.Env()
env_file = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_file):
    environ.Env.read_env(env_file=env_file) 

# Railway environment detection
RAILWAY_ENVIRONMENT = os.environ.get('RAILWAY_ENVIRONMENT', None)
IS_RAILWAY = RAILWAY_ENVIRONMENT is not None

# ===========================
# CONFIGURACIÓN DE SEGURIDAD
# ===========================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False) if not IS_RAILWAY else False

# Hosts permitidos
ALLOWED_HOSTS = ["*"]

# ===========================
# APLICACIONES
# ===========================

INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Necesario para django-allauth
    
    # Extensiones Django
    'django_extensions',
    
    # UI y Forms
    'crispy_forms',
    'crispy_bootstrap4',
    
    # Autenticación y OAuth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',  # Google OAuth
    
    # API y CORS
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',  # Autenticación con token
    # NOTA: 'rest_framework_simplejwt' está comentado pero configurado abajo
    
    # Apps del proyecto
    'usuarios',      # Gestión de usuarios y roles
    'viviendas',     # Edificios, viviendas y residentes
    'accesos',       # Control de visitas y movimientos
    'personal',      # Empleados y gestión de personal
    'financiero',    # Cuotas, pagos y finanzas
    'reportes',      # Generación de reportes
    'alertas',       # Sistema de alertas
]

# ===========================
# MIDDLEWARE
# ===========================

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',        # CORS - debe ser primero
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # Archivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware', # AllAuth
]

# ===========================
# CONFIGURACIÓN CORS
# ===========================

# CORS origins permitidos (para desarrollo con frontend separado)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # NextJS/React por defecto
    "http://127.0.0.1:3000",
    "http://localhost:8080",  # Alternativo
]

# Permite credenciales (cookies, headers de auth)
CORS_ALLOW_CREDENTIALS = True

# Headers permitidos en requests CORS
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Métodos HTTP permitidos
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Agregar dominio de producción aquí cuando sea necesario
    # "https://tudominio.com",
]

# ===========================
# CONFIGURACIÓN DE URLS Y TEMPLATES
# ===========================

ROOT_URLCONF = 'condominio_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'usuarios.context_processors.clientes_potenciales_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'condominio_app.wsgi.application'

# ===========================
# CONFIGURACIÓN DE BASE DE DATOS
# ===========================

# Configuración SQLite para desarrollo (comentada pero disponible)
""" 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
} 
"""

# PostgreSQL configuration
if IS_RAILWAY:
    # Railway PostgreSQL - usar DATABASE_URL si está disponible
    import dj_database_url
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        DATABASES = {
            'default': dj_database_url.parse(DATABASE_URL)
        }
    else:
        # Fallback usando variables individuales de Railway
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ.get("PGDATABASE", "railway"),
                'USER': os.environ.get("PGUSER", "postgres"),
                'PASSWORD': os.environ.get("PGPASSWORD", ""),
                'HOST': os.environ.get("PGHOST", "localhost"),
                'PORT': os.environ.get("PGPORT", "5432"),
            }
        }
else:
    # Configuración local de PostgreSQL
    os.environ.setdefault("PGDATABASE", "condominio_app_db")
    os.environ.setdefault("PGUSER", "postgres")
    os.environ.setdefault("PGPASSWORD", "root")
    os.environ.setdefault("PGHOST", "localhost")
    os.environ.setdefault("PGPORT", "5432")

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ["PGDATABASE"],
            'USER': os.environ["PGUSER"],
            'PASSWORD': os.environ["PGPASSWORD"],
            'HOST': os.environ["PGHOST"],
            'PORT': os.environ["PGPORT"],
        }
    }

# Configuración alternativa comentada (disponible si se necesita)
""" 
POSTGRES_LOCALLY = False
if ENVIRONMENT == 'production' or POSTGRES_LOCALLY == True:
    DATABASES['default'] = dj_database_url.parse(env('DATABASE_URL'))
"""

# ===========================
# VALIDACIÓN DE CONTRASEÑAS
# ===========================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ===========================
# INTERNACIONALIZACIÓN
# ===========================

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_L10N = True  # NOTA: Deprecado en Django 5.0+ pero mantenido para compatibilidad
USE_TZ = True

# ===========================
# ARCHIVOS ESTÁTICOS Y MEDIA
# ===========================

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# WhiteNoise configuration for static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (user uploads)
MEDIA_URL = '/mediafiles/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# ===========================
# CONFIGURACIÓN DE AUTENTICACIÓN
# ===========================

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'usuarios.Usuario'

# URLs de login/logout
LOGIN_REDIRECT_URL = 'dashboard'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'

# Backends de autenticación
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',           # Autenticación estándar
    'allauth.account.auth_backends.AuthenticationBackend', # AllAuth
]

# ===========================
# DJANGO ALLAUTH CONFIGURACIÓN
# ===========================

SITE_ID = 1

# AllAuth settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_UNIQUE_EMAIL = True

# Google OAuth configuration
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}

# ===========================
# CONFIGURACIÓN DE EMAIL
# ===========================

if IS_RAILWAY:
    # Configuración SMTP para producción
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = env.int('EMAIL_PORT', default=587)
    EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
    EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
    DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='Sistema Torre Segura <no-reply@torresegura.com>')
else:
    # Para desarrollo - mostrar emails en consola
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ===========================
# UI FRAMEWORKS
# ===========================

# Crispy Forms configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"

# ===========================
# API REST FRAMEWORK
# ===========================

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # JWT (disponible)
        'rest_framework.authentication.SessionAuthentication',         # Sesión
        'rest_framework.authentication.TokenAuthentication',           # Token
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# ===========================
# JWT CONFIGURATION (Simple JWT)
# ===========================

# NOTA: Configuración para djangorestframework_simplejwt (disponible pero no instalado actualmente)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ===========================
# CONFIGURACIÓN DE LOGGING
# ===========================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO' if IS_RAILWAY else 'DEBUG',
    },
    'loggers': {
        'corsheaders': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ===========================
# CONFIGURACIÓN DE SEGURIDAD PARA PRODUCCIÓN
# ===========================

if IS_RAILWAY:
    # Security settings for Railway deployment
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = False  # Railway maneja SSL automáticamente
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# ===========================
# OTRAS CONFIGURACIONES
# ===========================

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'