"""
Django settings for lumet_backend project.

Production-structured, configured for development.
Toda la configuración sensible se lee desde variables de entorno (.env).
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# Carga de variables de entorno desde .env (no sobrescribe variables ya definidas en el sistema)
env = environ.Env(
    DEBUG=(bool, False),
    CSRF_COOKIE_SECURE=(bool, False),
    SESSION_COOKIE_SECURE=(bool, False),
)
environ.Env.read_env(BASE_DIR / ".env")

# ─── Seguridad y entorno ───────────────────────────────────────────────────
SECRET_KEY = env("SECRET_KEY", default="changeme-in-production")

DEBUG = env("DEBUG")

# Hosts/dominios permitidos (separados por coma en .env). Vacío = todos (*) en dev.
_allowed = env.list("ALLOWED_HOSTS", default=[])
ALLOWED_HOSTS = _allowed if _allowed else ["*"]

# CSRF: orígenes confiables (separados por coma). Ej: https://app.ejemplo.com,https://api.ejemplo.com
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# Cookies solo por HTTPS en producción (poner True en .env en producción)
CSRF_COOKIE_SECURE = env("CSRF_COOKIE_SECURE")
SESSION_COOKIE_SECURE = env("SESSION_COOKIE_SECURE")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "drf_spectacular",
    "apps.core",
    "apps.persona",
    "apps.auth",
    "apps.empresa",
    "apps.servicio",
    "apps.formularios",
    "apps.cliente",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "config" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ─── Base de datos (PostgreSQL) ─────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", default="lumet_db"),
        "USER": env("DB_USER", default="lumet_user"),
        "PASSWORD": env("DB_PASSWORD", default="lumet_pass"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-es"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

# Media: archivos subidos por usuarios (PDFs, etc.)
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "persona.Persona"

# ─── REST Framework ────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "config.pagination.StandardPagination",
    "PAGE_SIZE": env.int("API_PAGE_SIZE", default=20),
}

SPECTACULAR_SETTINGS = {
    "TITLE": env("API_TITLE", default="Lumet API"),
    "DESCRIPTION": env(
        "API_DESCRIPTION",
        default="API REST de Lumet. Autenticación por correo + código y JWT.",
    ),
    "VERSION": env("API_VERSION", default="1.0.0"),
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": r"/api/docs",
}

# ─── Simple JWT ─────────────────────────────────────────────────────────────
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=env.int("SIMPLE_JWT_ACCESS_TOKEN_HOURS", default=10)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("SIMPLE_JWT_REFRESH_TOKEN_DAYS", default=7)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ─── CORS ──────────────────────────────────────────────────────────────────
# Con DEBUG=True se permiten todos los orígenes; con DEBUG=False se usan CORS_ALLOWED_ORIGINS.
CORS_ALLOW_ALL_ORIGINS = DEBUG
_cors_origins = env.list("CORS_ALLOWED_ORIGINS", default=["http://localhost:3000", "http://127.0.0.1:3000"])
CORS_ALLOWED_ORIGINS = _cors_origins

# ─── Autenticación: tiempos de expiración (segundos) ────────────────────────
LOGIN_CODE_TIMEOUT = env.int("LOGIN_CODE_TIMEOUT", default=600)  # código OTP login (default 10 min)
PWD_RESET_TOKEN_TIMEOUT = env.int("PWD_RESET_TOKEN_TIMEOUT", default=300)  # token cambio contraseña (default 5 min)

# ─── Email (dev: consola; prod: Resend o SMTP vía .env) ─────────────────────
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@lumet.local")

# Resend (producción): API key desde .env. Si está definida, el servicio de correo usará Resend.
RESEND_API_KEY = env("API_KEY_RESEND", default=None) or None
RESEND_FROM_EMAIL = env("RESEND_FROM_EMAIL", default=DEFAULT_FROM_EMAIL)
RESEND_SANDBOX_FROM = env("RESEND_SANDBOX_FROM", default="Lumet <onboarding@resend.dev>")
LUMET_LOGO_URL = env("LUMET_LOGO_URL", default=None) or None

# ─── Cache (códigos de login: memoria en dev; en prod puede ser Redis) ──────
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "OPTIONS": {"MAX_ENTRIES": env.int("CACHE_MAX_ENTRIES", default=1000)},
    }
}
