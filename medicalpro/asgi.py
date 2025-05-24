"""
ASGI config for medicalpro project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicalpro.settings')

# Import websocket URLs after environment is configured
import medicalpro.core.routing

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            medicalpro.core.routing.websocket_urlpatterns
        )
    ),
}) 