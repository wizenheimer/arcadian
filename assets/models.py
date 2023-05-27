from django.db import models
from accounts.models import Workspace


class DataSource(models.Model):
    """
    Refers Source of data
    ----------------------------------------------------------------
    source: Stripe, Google Play Store and Apple App Store]
    expiration: Denotes the time for which credentials will expire
    """

    SOURCE_TYPE = (
        ("Google Play Store", "Google Play Store"),
        ("App Store", "App Store"),
        ("Stripe", "Stripe"),
        ("Self Reported", "Self Reported"),
    )
    source = models.CharField(
        max_length=255,
        choices=SOURCE_TYPE,
        default="Self Reported",
    )
    # TODO: add validators for this field
    key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    # TODO: add utils for this field
    # if key is verified
    is_verified = models.BooleanField(
        default=False,
    )
    # workspace the data source is part of
    workspace = models.ForeignKey(
        Workspace,
        related_name="datasources",
        on_delete=models.CASCADE,
    )
    # metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}"


class DataRepository(models.Model):
    """
    Holds all data for a given workspace.
    ----------------------------------------------------------------
    """

    # workspace the data repository is part of
    workspace = models.ForeignKey(
        Workspace,
        related_name="repositories",
        on_delete=models.CASCADE,
    )
    # metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}"


class Folder(models.Model):
    """
    Holds all Folder objects for a given repository.
    ----------------------------------------------------------------
    """

    name = models.CharField(max_length=255)
    repository = models.ForeignKey(
        DataRepository,
        related_name="folders",
        on_delete=models.CASCADE,
    )
    # denotes the parent folder
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )

    def __str__(self):
        return self.name


class File(models.Model):
    """
    Holds all the files for a given folder.
    ----------------------------------------------------------------
    """

    # TODO: add S3 file fields here

    name = models.CharField(max_length=255)
    # folder the file belongs to
    folder = models.ForeignKey(
        Folder,
        on_delete=models.CASCADE,
        related_name="files",
    )

    def __str__(self):
        return self.name
