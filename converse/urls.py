from django.urls import path, include
from rest_framework.routers import DefaultRouter
from converse.views import ConversationViewset, MessageViewset

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(
    r"conversation",
    ConversationViewset,
    basename="conversation",
)
router.register(
    r"messages",
    MessageViewset,
    basename="messages",
)

urlpatterns = [
    # The API URLs are now determined automatically by the router.
    path("", include(router.urls)),
]
