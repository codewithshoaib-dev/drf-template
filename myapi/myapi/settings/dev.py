from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CORS_ALLOW_ALL_ORIGINS = True

SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = timedelta(minutes=60)
SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'] = timedelta(days=7)


LOGGING['root']['level'] = 'DEBUG'