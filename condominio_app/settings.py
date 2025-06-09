import os
from pathlib import Path
from datetime import timedelta
import environ
import socket
import dj_database_url


hostname = socket.gethostname()

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(env_file=os.path.join(BASE_DIR, '.env')) 
ENVIRONMENT = env('ENVIRONMENT', default='production')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')


# SECURITY WARNING: don't run with debug turned on in production
if ENVIRONMENT == 'production':
    DEBUG = True
else:
    DEBUG = False

DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = ["*"]
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Necesario para django-allauth
    'django_extensions',
    

    'crispy_forms',
    'crispy_bootstrap4',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',  # Proveedor de Google
    'corsheaders',
    'rest_framework',
    # 'rest_framework_simplejwt',  # Para JWT
    'rest_framework.authtoken',  # Para autenticación con token
    
    # Apps propias
    'usuarios',
    'viviendas',
    'accesos',
    'personal',  
    'financiero',
    'reportes',
    'alertas',  # Aplicación de alertas
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Debe ser el primero
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Middleware de AllAuth 
]
# Para desarrollo (permite todo desde localhost)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # NextJS por defecto
    "http://127.0.0.1:3000",
    "http://localhost:3001",  # Por si usas otro puerto
]

# Permite credenciales (cookies, headers de auth)
CORS_ALLOW_CREDENTIALS = True
ROOT_URLCONF = 'condominio_app.urls'


# Headers permitidos
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


# e
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

POSTGRES_LOCALLY = False
if ENVIRONMENT ==  'production' or POSTGRES_LOCALLY == True:
    DATABASES['default'] = dj_database_url.parse(env('DATABASE_URL'))

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/mediafiles/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# User model personalizado
AUTH_USER_MODEL = 'usuarios.Usuario'

# Configuración de login
LOGIN_REDIRECT_URL = 'dashboard'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}



# ====== CONFIGURACIÓN DE CSRF (para vistas sin autenticación) ======
# Estas URLs estarán exentas de verificación CSRF
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Agrega tu dominio de producción aquí
    # "https://tudominio.com",
]
# ====== CONFIGURACIÓN DE LOGGING PARA DEBUG ======
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'corsheaders': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}
# Django AllAuth configuración
AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

if "torresegura" in hostname:
    SITE_ID = 1  # Sitio móvil
else:
    SITE_ID = 2  # Sitio escritorio

# Configuración de AllAuth
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False

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
        'LOCALE_FUNC': lambda request: 'en_US',
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

SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_ADAPTER = 'usuarios.adapters.CustomSocialAccountAdapter'  # Opcional para personalizar el proceso

# Reemplaza con las credenciales reales de tu aplicación de Google
GOOGLE_CLIENT_ID = '54385706918-qqe70jbg6pvo897o0970kmmfs5hbg44g.apps.googleusercontent.com'
GOOGLE_SECRET = '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'

# Notificaciones con mensajes
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Configuración de correo para desarrollo
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Para desarrollo, los correos se mostrarán en la consola
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
# Para producción, usa esto:
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='Sistema <no-reply@dominio.com>')
