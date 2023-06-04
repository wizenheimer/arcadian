from channels.generic.websocket import AsyncWebsocketConsumer


class ConversationConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        # TODO: initialize agents
        # TODO: load previous conversation into agent's context
        super().__init__(*args, **kwargs)

    async def connect(self):
        # TODO: get chat id from client
        # TODO: create or fetch agent for the conversation
        await self.accept()

    async def disconnect(self, close_code):
        await self.close()

    async def receive(self, text_data):
        # TODO: save client text to db
        # TODO: call the agent for a response
        # TODO: save agent's text to db
        # TODO: send message back to the client
        await self.send(text_data)
