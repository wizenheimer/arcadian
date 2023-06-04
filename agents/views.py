from rest_framework import viewsets
from agents.models import AgentCollection, Agents
from agents.serializers import AgentSerializer, AgentCollectionSerializer


class AgentViewset(viewsets.ModelViewSet):
    queryset = Agents.objects.all()
    serializer_class = AgentSerializer


class AgentCollectionViewset(viewsets.ModelViewSet):
    queryset = AgentCollection.objects.all()
    serializer_class = AgentCollectionSerializer
