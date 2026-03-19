"""
Django settings for lumet_backend project.

Configuración minimalista y lista para producción.
Toda la configuración sensible se lee desde variables de entorno (.env).
"""

from pathlib import Path
from urllib.parse import urlparse

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# Carga de variables de entorno desde .env (no sobrescribe variables ya definidas en el sistema).
# Nota: mantenemos SOLO las variables necesarias en el .env final.
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CORS_ALLOWED_ORIGINS=(list, []),
    CSRF_TRUSTED_ORIGINS=(list, []),
    LOGIN_CODE_TIMEOUT=(int, 600),
    PWD_RESET_TOKEN_TIMEOUT=(int, 300),
    SIMPLE_JWT_ACCESS_TOKEN_HOURS=(int, 10),
    SIMPLE_JWT_REFRESH_TOKEN_DAYS=(int, 30),
    DB_PORT=(int, 5432),
)
environ.Env.read_env(BASE_DIR / ".env")

# ─── Seguridad y entorno ───────────────────────────────────────────────────
SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG")

FRONTEND_URL = env("FRONTEND_URL")


def _normalize_origin(url: str) -> str:
    """
    Convierte una URL (con o sin path) a un origen: https://host.
    """

    parsed = urlparse(url)
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc or parsed.path  # por si llega como "www.ejemplo.com"
    netloc = netloc.split("/")[0]
    return f"{scheme}://{netloc}".rstrip("/")


frontend_origin = _normalize_origin(FRONTEND_URL)

# Hosts/dominios permitidos (separados por coma en .env).
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
if DEBUG:
    # En desarrollo evitamos fricciones con host headers.
    ALLOWED_HOSTS = ["*"]

# CSRF: orígenes confiables (separados por coma). Default = FRONTEND_URL.
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[frontend_origin])

# Cookies: habilita cross-domain de forma segura (SameSite=None + Secure en producción).
SESSION_COOKIE_DOMAIN = env("SESSION_COOKIE_DOMAIN", default=None) or None
CSRF_COOKIE_DOMAIN = env("CSRF_COOKIE_DOMAIN", default=None) or None
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = "None" if not DEBUG else "Lax"
CSRF_COOKIE_SAMESITE = "None" if not DEBUG else "Lax"

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
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
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
    "PAGE_SIZE": 20,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Lumet API",
    "DESCRIPTION": "API REST de Lumet. Autenticación por correo + código y JWT.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": r"/api/docs",
}

# ─── Simple JWT ─────────────────────────────────────────────────────────────
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=env.int("SIMPLE_JWT_ACCESS_TOKEN_HOURS", default=10)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("SIMPLE_JWT_REFRESH_TOKEN_DAYS", default=30)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ─── CORS ──────────────────────────────────────────────────────────────────
# En producción se usan CORS_ALLOWED_ORIGINS (default = FRONTEND_URL).
# Importante: con cross-domain + cookies, CORS debe permitir credenciales.
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[frontend_origin])

# ─── Autenticación: tiempos de expiración (segundos) ────────────────────────
LOGIN_CODE_TIMEOUT = env.int("LOGIN_CODE_TIMEOUT", default=600)  # código OTP login (default 10 min)
PWD_RESET_TOKEN_TIMEOUT = env.int("PWD_RESET_TOKEN_TIMEOUT", default=300)  # token cambio contraseña (default 5 min)

# ─── Email (Resend) ────────────────────────────────────────────────────────
RESEND_API_KEY = env("RESEND_API_KEY", default=None) or None
RESEND_FROM_EMAIL = env("RESEND_FROM_EMAIL")
DEFAULT_FROM_EMAIL = RESEND_FROM_EMAIL

# Mantener compatibilidad con la plantilla de OTP.
LUMET_LOGO_URL = None

# ─── Cache (códigos de login: memoria en dev; en prod puede ser Redis) ──────
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "OPTIONS": {"MAX_ENTRIES": 1000},
    }
}
