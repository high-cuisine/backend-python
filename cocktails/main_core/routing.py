from django.urls import re_path
from apps.channel import consumers

websocket_urlpatterns = [
    re_path(r'ws/support/$', consumers.TicketConsumer.as_asgi()),
]
