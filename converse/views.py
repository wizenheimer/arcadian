from rest_framework import viewsets
from converse.models import Conversation, Message
from converse.serializers import MessageSerializer, ConversationSerializer


class ConversationViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer


class MessageViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
