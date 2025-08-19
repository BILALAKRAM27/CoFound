"""
ASGI config for CoFound project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

# Ensure settings are configured before importing Django/Channels modules that rely on them
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CoFound.settings')

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Initialize Django ASGI application early to populate app registry
django_asgi_app = get_asgi_application()

# Import routing after settings and Django app are initialized
import Entrepreneurs.routing

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            Entrepreneurs.routing.websocket_urlpatterns
        )
    ),
})
