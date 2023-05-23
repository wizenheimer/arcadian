from email.policy import default
from django.db import models
from django.contrib.auth.models import AbstractUser
from accounts.managers import UserManager


class Workspace(models.Model):
    """
    Workspace models represent the user collective
    """

    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title


class User(AbstractUser):
    """
    Custom user models
    """

    username = None
    email = models.EmailField(unique=True, db_index=True)
    # has verified email address
    is_verified = models.BooleanField(default=False)
    # has an active account
    is_active = models.BooleanField(default=False)
    # metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # relationship
    workspace = models.ForeignKey(
        Workspace,
        related_name="users",
        on_delete=models.CASCADE,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return str(self.email)


class WorkspaceAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    # workspace roles
    is_manager = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_member = models.BooleanField(default=True)
    is_billing = models.BooleanField(default=False)

    def __str__(self):
        return super().id
