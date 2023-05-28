from django.urls import path, include
from rest_framework.routers import DefaultRouter
from agents.views import AgentCollectionViewset, AgentViewset

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(
    r"agents",
    AgentViewset,
    basename="agents",
)
router.register(
    r"collections",
    AgentCollectionViewset,
    basename="collections",
)

urlpatterns = [
    # The API URLs are now determined automatically by the router.
    path("", include(router.urls)),
]
