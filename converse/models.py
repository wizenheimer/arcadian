import tiktoken
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from accounts.models import User
from agents.models import Agents
from assets.models import File


class Conversation(models.Model):
    """
    Model representing a conversation
    """

    STATE = (
        ("active", "active"),
        ("archive", "archive"),
        ("favourite", "favourite"),
    )
    # TODO: gpt3.5 model for summarizing conversation
    title = models.CharField(
        max_length=255,
        default="New Conversation",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    agent = models.ForeignKey(
        Agents,
        on_delete=models.CASCADE,
    )
    document = models.ForeignKey(
        File,
        on_delete=models.CASCADE,
    )
    # determines whether the conversation should be marked as favorite, active or archived
    conversation_state = models.CharField(
        max_length=255,
        choices=STATE,
        default="active",
    )

    def __str__(self):
        return f"{self.id}"


class Message(models.Model):
    """
    Model representing the message associated with a conversation
    """

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    # TODO: generic foreign key that could be a file field or a text field, since GPT 4 is multi-modal
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # TODO: alter the conversation and follow from that point on
    replied_to = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="replies",
    )
    # Generic foreign key pointing to the message sender: User or Agent
    sender_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )
    sender_id = models.PositiveIntegerField()
    sender = GenericForeignKey("sender_type", "sender_id")

    class Meta:
        ordering = ["-created_at"]

    def calculate_token(self):
        """
        Calculates the token for the message
        """
        conversation = self.conversation
        agent = conversation.agent.all()[0]
        model_type = agent.embedding_model_type
        encoding = tiktoken.encoding_for_model(model_type)
        num_tokens = len(encoding.encode(self.content))
        return num_tokens

    def __str__(self):
        return f"{self.id}"
