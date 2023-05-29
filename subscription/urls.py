from django.urls import path, include
from rest_framework.routers import DefaultRouter
from subscription.views import SubscriptionViewset

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(
    r"subscription",
    SubscriptionViewset,
    basename="subscription",
)

urlpatterns = [
    # The API URLs are now determined automatically by the router.
    path("", include(router.urls)),
]
