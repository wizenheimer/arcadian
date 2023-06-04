from channels.generic.websocket import AsyncWebsocketConsumer
from langchain.agents import AgentExecutor
from converse.loader import ConversationRepository
from agents.factory import AgentFactory
import json


class ConversationConsumer(AsyncWebsocketConsumer):
    agent: AgentExecutor

    def __init__(self, *args, **kwargs):
        self.agent_factory = AgentFactory()
        self.conversation_repository = ConversationRepository()
        super().__init__(*args, **kwargs)

    async def connect(self):
        # get chat id from client
        conversation_id = self.scope["url_route"]["kwargs"].get("conversation_id")

        # create or fetch agent for the conversation
        self.agent = await self.agent_factory.create_agent(
            conversation_id=conversation_id,
        )

        await self.accept()

    async def disconnect(self):
        await self.close()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        conversation_id = text_data_json["conversation_id"]
        # TODO: phase away user id
        user_id = text_data_json["user_id"]

        # Forward the message to LangChain
        response = await self.message_agent(message, conversation_id, user_id)

        # Send the response back to the client
        await self.send(text_data=json.dumps({"message": response, "type": "answer"}))

        await self.send(text_data)

    async def message_agent(
        self,
        message,
        conversation_id,
        user_id,
    ):
        # Save the user message to the database
        await self.conversation_repository.save_message(
            sender_id=user_id,
            content=message,
            sender="User",
            conversation_id=conversation_id,
        )

        # Call the agent
        response = await self.agent.arun(message)

        # Save the AI message to the database
        await self.conversation_repository.save_message(
            sender_id=user_id,
            content=response,
            sender="Agent",
            conversation_id=conversation_id,
        )

        return response
