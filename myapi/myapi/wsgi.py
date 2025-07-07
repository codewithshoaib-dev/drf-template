
import os

from django.core.wsgi import get_wsgi_application

app_env = os.getenv('APP_ENV', 'dev')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'myapi.settings.{app_env}')

application = get_wsgi_application()
