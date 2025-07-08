from .base import *
from django.core.exceptions import ImproperlyConfigured
import environ

def get_env_setting(setting):
    env = environ.Env()
    environ.Env.read_env()
    value = env(setting)
    if value is None:
        raise ImproperlyConfigured(f"Missing required env var: {setting}")
    return value

DEBUG = False

SECRET_KEY = get_env_setting("SECRET_KEY")

ALLOWED_HOSTS = get_env_setting("ALLOWED_HOSTS").split(",")


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_env_setting('POSTGRES_DB'),
        'USER': get_env_setting('POSTGRES_USER'),
        'PASSWORD': get_env_setting('POSTGRES_PASSWORD'),
        'HOST': get_env_setting('POSTGRES_HOST'),
        'PORT': get_env_setting('POSTGRES_PORT'),
    }
}

CORS_ALLOWED_ORIGINS = get_env_setting("CORS_ALLOWED_ORIGINS").split(",")


SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = timedelta(minutes=15)

SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'] = timedelta(days=1)


# Security hardening
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = get_env_setting("SECURE_SSL_REDIRECT") == "True"
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True


# Static & Media
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'



LOGGING['handlers']['console']['formatter'] = 'verbose'
LOGGING['root']['level'] = 'WARNING'

LOGGING['handlers']['file'] = {
    'level': 'INFO',
    'class': 'logging.FileHandler',
    'filename': BASE_DIR / 'logs/app.log',
    'formatter': 'verbose',
}

LOGGING['loggers'] = {
    'django': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
        'propagate': False,
    },
    'django.request': {
        'handlers': ['console', 'file'],
        'level': 'ERROR',
        'propagate': False,
    },
}
