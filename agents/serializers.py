from rest_framework import serializers
from agents.models import Agent, AgentCollection


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = "__all__"


class AgentCollection(serializers.ModelSerializer):
    agents = serializers.SerializerMethodField()

    class Meta:
        model = AgentCollection
        fields = (
            "id",
            "agents",
            "created_at",
            "updated_at",
        )

    def get_agents(self, collection):
        agents = collection.agents.all()
        serializer = AgentSerializer(agents, many=True)
        return serializer.data
