from rest_framework import viewsets
from converse.models import Conversation, Message
from converse.serializers import MessageSerializer, ConversationSerializer


class ConversationViewset(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
