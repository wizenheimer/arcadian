from channels.db import database_sync_to_async
from converse.models import Conversation, Message
from agents.models import Agent
from accounts.models import User
from django.contrib.contenttypes.models import ContentType


class ConversationRepository:
    """
    Class for interacting with conversation
    """

    @database_sync_to_async
    def get_messages(
        self,
        conversation_id,
        order_by="created_at",
    ):
        """
        Retrieve the messages for the given conversation from the database
        """
        conversation = Conversation.objects.get(id=conversation_id)
        messages = conversation.messages.all().order_by(order_by)
        return messages

    @database_sync_to_async
    def save_message(
        self,
        content,
        conversation_id,
        sender_id,
        sender_type="Agent",
    ):
        conversation = Conversation.objects.get(id=conversation_id)
        if sender_type == "Agent":
            sender_type = ContentType.objects.get_for_model(Agent)
        else:
            sender_type = ContentType.objects.get_for_model(User)
        # Save the message to the database
        Message.objects.create(
            sender_id=sender_id,
            sender_type=sender_type,
            content=content,
            conversation=conversation,
        )
