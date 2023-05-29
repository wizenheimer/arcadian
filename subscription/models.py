from django.db import models
from accounts.models import Workspace


class Subscription(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=255)
    stripe_customer_id = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id}"
