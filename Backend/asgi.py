"""
ASGI config for Backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter # <- Add this
from channels.auth import AuthMiddlewareStack # <- Add this
from managequeue.consumers import QueueConsumer # <- Add this

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')


application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            QueueConsumer.as_asgi()
        ),
    }
)