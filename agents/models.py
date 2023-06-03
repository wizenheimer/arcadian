from email.policy import default
from random import choices
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

    MODEL_TYPE = (
        ("CohereAI", "CohereAI"),
        # TODO: add ability for using other models for making embeddings
        ("OpenAI", "OpenAI"),
        ("HuggingFace", "HuggingFace"),
        # TODO: add ability for using finetuned model for making requests
    )

    # describes which foundational model does the agent collection belongs to
    model_type = models.CharField(
        max_length=255,
        choices=MODEL_TYPE,
        default="CohereAI",
    )

    # TODO: add validators for this field depending on model type
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
    # determines whether the collection is active or not
    is_active = models.BooleanField(default=True)
    # TODO: add option for usage caps based on tokens

    def __str__(self):
        return f"{self.id}"


class Agents(models.Model):
    """
    Agents belonging to a specific foundational model
    """

    GENERATIVE_MODEL = (
        # Open AI Models
        ("gpt-4", "gpt-4"),
        ("gpt-3.5-turbo", "gpt-3.5-turbo"),
        ("text-davinci-002", "text-davinci-002"),
        ("text-davinci-003", "text-davinci-003"),
        # Cohere AI Models
        ("command", "command"),
        ("command-light", "command-light"),
        ("command-nightly", "command-nightly"),
        ("command-light-nightly", "command-light-nightly"),
        ("base-light", "base-light"),
        ("base", "base"),
        # Other Models
        ("others", "others"),
    )
    EMBEDDING_MODEL = (
        # Open AI Models
        ("text-embedding-ada-002", "text-embedding-ada-002"),
        # Cohere AI Models
        ("embed-english-v2.0", "embed-english-v2.0"),
        ("embed-english-light-v2.0", "embed-english-light-v2.0"),
        ("embed-multilingual-v2.0", "embed-multilingual-v2.0"),
    )
    title = models.CharField(max_length=255)
    collection = models.ForeignKey(
        AgentCollection,
        related_name="agents",
        on_delete=models.CASCADE,
    )
    generative_model_type = models.CharField(
        max_length=255,
        choices=GENERATIVE_MODEL,
        default="base-light",
    )
    embedding_model_type = models.CharField(
        max_length=255,
        choices=EMBEDDING_MODEL,
        default="embed-english-light-v2.0",
    )

    def __str__(self):
        return f"{self.id}"
