from random import choice
from string import ascii_uppercase
from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.managers import UserManager


class Workspace(models.Model):
    """
    Workspace models represent the user collective
    Note:
    - A user can be part of multiple workspaces
    """

    title = models.CharField(max_length=255)
    description = models.TextField()

    # metadata
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    # token for creating invites
    token = models.CharField(max_length=255, db_index=True, null=True, blank=True)

    def update_token(self):
        # update token for the given model
        self.token = "".join(choice(ascii_uppercase) for i in range(16))
        return self.token

    def get_token(self):
        return self.token

    def save(self, *args, **kwargs):
        # create a new token
        token = self.update_token()
        super(Workspace, self).save(*args, **kwargs)

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

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    def get_access_token(self):
        return str(RefreshToken.for_user(self).access_token)

    def get_refresh_token(self):
        return str(RefreshToken.for_user(self))

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
    # counterparty roles
    is_counterparty = models.BooleanField(default=False)

    def __str__(self):
        return super().id
