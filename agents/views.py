from rest_framework import viewsets
from agents.models import AgentCollection, Agents
from agents.serializers import AgentSerializer, AgentCollectionSerializer


class AgentViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Agents.objects.all()
    serializer_class = AgentSerializer


class AgentCollectionViewset(viewsets.ReadOnlyModelViewSet):
    queryset = AgentCollection.objects.all()
    serializer_class = AgentCollectionSerializer
