"""
Configuración de Django para PRODUCCIÓN
Incluye seguridad, logging, caché, y monitoreo
"""
import os
from .base import *

# ============================================================================
# SEGURIDAD CRÍTICA
# ============================================================================

# DEBUG DEBE estar False en producción
DEBUG = False

# SECRET_KEY DEBE venir de variable de entorno (OBLIGATORIO)
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY or SECRET_KEY == "django-insecure-change-me":
    raise ValueError(
        "🚨 SEGURIDAD CRÍTICA: La variable de entorno SECRET_KEY no está configurada.\n"
        "En producción es OBLIGATORIA.\n"
        "Ejecuta: export SECRET_KEY='<tu-clave-aleatoria-larga>'"
    )

# ALLOWED_HOSTS - DEBE estar configurado en producción
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['']:
    raise ValueError(
        "🚨 SEGURIDAD CRÍTICA: ALLOWED_HOSTS no está configurado.\n"
        "Ejecuta: export ALLOWED_HOSTS='tudominio.com,www.tudominio.com'"
    )

# ============================================================================
# COOKIES Y SESIONES (HTTPS)
# ============================================================================

# Cookies solo se envían por HTTPS
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Cookies NO accesibles desde JavaScript (previene XSS)
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True

# SameSite para prevenir CSRF
CSRF_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_SAMESITE = 'Strict'

# Redirigir HTTP → HTTPS
SECURE_SSL_REDIRECT = True

# ============================================================================
# HSTS (HTTP Strict Transport Security)
# ============================================================================

# Fuerza HTTPS por 1 año
SECURE_HSTS_SECONDS = 31536000  # 1 año

# Incluir subdomios
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Agregar a lista de preload de Chrome/Firefox
SECURE_HSTS_PRELOAD = True

# ============================================================================
# X-FRAME-OPTIONS (Previene clickjacking)
# ============================================================================

X_FRAME_OPTIONS = 'DENY'

# ============================================================================
# CONTENT SECURITY POLICY
# ============================================================================

SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"),
    "style-src": ("'self'", "'unsafe-inline'", "fonts.googleapis.com", "cdn.jsdelivr.net"),
    "img-src": ("'self'", "data:", "https:"),
    "font-src": ("'self'", "fonts.gstatic.com"),
    "connect-src": ("'self'",),
}

# ============================================================================
# CORS y CSRF
# ============================================================================

# Orígenes confiables para CORS
CORS_TRUSTED_ORIGINS = os.environ.get('CORS_TRUSTED_ORIGINS', '').split(',')

# Orígenes confiables para CSRF
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')

# ============================================================================
# BASE DE DATOS - Connection Pooling
# ============================================================================

# Mantener conexiones activas 10 minutos
DATABASES['default']['CONN_MAX_AGE'] = 600

# Transacciones atómicas (más seguro)
DATABASES['default']['ATOMIC_REQUESTS'] = True

# ============================================================================
# CACHÉ CON REDIS
# ============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_CACHE_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50},
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        }
    }
}

# Usar caché para sesiones
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# ============================================================================
# LOGGING EN PRODUCCIÓN
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
            'datefmt': '%d/%m/%Y %H:%M:%S',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        }
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/football_analytics/django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 10,
            'formatter': 'json',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/football_analytics/error.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 10,
            'formatter': 'json',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ============================================================================
# CELERY EN PRODUCCIÓN
# ============================================================================

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/0')

# Serializar con JSON (más seguro)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Timeout para tareas (30 minutos)
CELERY_TASK_TIME_LIMIT = 30 * 60

# ============================================================================
# EMAIL EN PRODUCCIÓN
# ============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@football-analytics.com')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'server@football-analytics.com')

# ============================================================================
# ARCHIVOS ESTÁTICOS Y MULTIMEDIA
# ============================================================================

# CloudFront o CDN para archivos estáticos
STATIC_URL = os.environ.get('STATIC_URL', '/static/')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Compresión de archivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Uploads
MEDIA_URL = os.environ.get('MEDIA_URL', '/media/')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ============================================================================
# SEGURIDAD ADICIONAL
# ============================================================================

# Permitir solo métodos HTTP seguros
ALLOWED_HTTP_METHODS = ('GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS')

# Timeout de sesión (30 minutos)
SESSION_COOKIE_AGE = 30 * 60

# Rate limiting (requiere django-ratelimit)
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB