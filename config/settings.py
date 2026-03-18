"""
Django settings for lumet_backend project.

Production-structured, configured for development.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'changeme-in-production')

DEBUG = os.getenv('DEBUG', '0') == '1'

# Hosts/dominios permitidos (separados por coma; * = todos en dev)
_allowed = os.getenv('ALLOWED_HOSTS', '').strip()
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(',') if h.strip()] if _allowed else ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',
    'apps.core',
    'apps.persona',
    'apps.auth',
    'apps.empresa',
    'apps.servicio',
    'apps.formularios',
    'apps.cliente',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'config' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database - PostgreSQL only
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'lumet_db'),
        'USER': os.getenv('DB_USER', 'lumet_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'lumet_pass'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

# Media: archivos subidos por usuarios (PDFs, etc.)
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'persona.Persona'

# REST Framework
def _int_env(name, default):
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'config.pagination.StandardPagination',
    'PAGE_SIZE': _int_env('API_PAGE_SIZE', 20),
}

SPECTACULAR_SETTINGS = {
    'TITLE': os.getenv('API_TITLE', 'Lumet API'),
    'DESCRIPTION': os.getenv('API_DESCRIPTION', 'API REST de Lumet. Autenticación por correo + código y JWT.'),
    'VERSION': os.getenv('API_VERSION', '1.0.0'),
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/docs',
}

# Simple JWT
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=_int_env('SIMPLE_JWT_ACCESS_TOKEN_HOURS', 10)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=_int_env('SIMPLE_JWT_REFRESH_TOKEN_DAYS', 7)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS (orígenes permitidos cuando DEBUG=False; separados por coma)
CORS_ALLOW_ALL_ORIGINS = DEBUG
_cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').strip()
CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_origins.split(',') if o.strip()] if _cors_origins else []

# Autenticación: tiempos de expiración (segundos)
LOGIN_CODE_TIMEOUT = _int_env('LOGIN_CODE_TIMEOUT', 600)  # código OTP login (default 10 min)
PWD_RESET_TOKEN_TIMEOUT = _int_env('PWD_RESET_TOKEN_TIMEOUT', 300)  # token para cambiar contraseña (default 5 min)

# Email (dev: consola; prod: Resend o SMTP en .env)
EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend',
)
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@lumet.local')

# Resend (producción): API key desde .env (API_KEY_RESEND). Si está definida, el servicio de correo usará Resend.
RESEND_API_KEY = os.getenv('API_KEY_RESEND', '').strip() or None
# Remitente para Resend (debe ser un correo/dominio verificado en Resend)
RESEND_FROM_EMAIL = os.getenv('RESEND_FROM_EMAIL', DEFAULT_FROM_EMAIL)
# Remitente de prueba Resend cuando el dominio no está verificado (.local, etc.)
RESEND_SANDBOX_FROM = os.getenv('RESEND_SANDBOX_FROM', 'Lumet <onboarding@resend.dev>').strip()
# URL del logo para plantillas de correo (opcional; si no se define, se muestra el texto "Lumet")
LUMET_LOGO_URL = os.getenv('LUMET_LOGO_URL', '').strip() or None

# Cache para códigos de login (memoria en dev; en prod puede ser Redis)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'OPTIONS': {'MAX_ENTRIES': _int_env('CACHE_MAX_ENTRIES', 1000)},
    }
}
