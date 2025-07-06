

import os

from django.core.asgi import get_asgi_application

app_env = os.getenv('APP_ENV', 'dev')
os.environ.setdefault(f'DJANGO_SETTINGS_MODULE', 'myapi.settings.dev')

application = get_asgi_application()
