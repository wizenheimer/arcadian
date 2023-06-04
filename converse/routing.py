from django.urls import re_path, path
from converse.consumers import ConversationConsumer

websocket_urlpatterns = [
    path("ws/chat/", ConversationConsumer.as_asgi()),
    # url for a given chat_id
    re_path(r"ws/chat/(?P<chat_id>\w+)/$", ConversationConsumer.as_asgi()),
]
