from django.db import models
from accounts.models import User
from agents.models import Agents


class Conversation(models.Model):
    """
    Model representing a conversation
    """

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
    # TODO: link the conversation to the document
    # TODO: remove these fields, doesn't seem necessary
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # determines whether the conversation should be marked as favorite
    favourite = models.BooleanField(default=False)
    # determines whether conversation is active or archived
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = [
            "created_at",
        ]

    def __str__(self):
        return f"{self.id}"


class Message(models.Model):
    # TODO: generic foreign key pointing to the creator: User or Agent
    # from = blahh blahh blahh
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

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.id}"
