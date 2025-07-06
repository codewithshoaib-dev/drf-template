
import os

from django.core.wsgi import get_wsgi_application

app_env = os.getenv('APP_ENV', 'dev')

os.environ.setdefault(f'DJANGO_SETTINGS_MODULE', 'myapi.settings.dev')

application = get_wsgi_application()
