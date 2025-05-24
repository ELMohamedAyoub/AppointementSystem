from django.urls import path

from medicalpro.core.consumers import NotificationConsumer

websocket_urlpatterns = [
    path('ws/notifications/', NotificationConsumer.as_asgi()),
] 