from django.shortcuts import render
from rest_framework import viewsets
from subscription.models import Subscription
from subscription.serializers import SubscriptionSerializer


class SubscriptionViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
