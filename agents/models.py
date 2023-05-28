from django.db import models
from django_cryptography.fields import encrypt
from accounts.models import Workspace


# TODO: build token calculator
# TODO: build usage caps for conversation = token calculator for agent collection * price per token
# TODO: add ability for using finetuned model for making requests


class AgentCollection(models.Model):
    """
    Agents belonging to a specific foundational model
    """

    # TODO: add validators for this field
    api_key = encrypt(
        models.CharField(
            max_length=255,
            null=True,
            blank=True,
        )
    )
    # workspace the agents are a part of
    workspace = models.ForeignKey(
        Workspace,
        related_name="agents",
        on_delete=models.CASCADE,
    )
    # metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.id}"


class Agents(models.Model):
    title = models.CharField(max_length=255)
    collection = models.ForeignKey(
        AgentCollection,
        related_name="agents",
        on_delete=models.CASCADE,
    )
