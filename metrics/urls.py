from django.urls import path, include
from rest_framework.routers import DefaultRouter
from metrics.views import MetricCollectionViewset, MetricViewset

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(
    r"metrics",
    MetricViewset,
    basename="metric",
)
router.register(
    r"collection",
    MetricCollectionViewset,
    basename="collection",
)

urlpatterns = [
    # The API URLs are now determined automatically by the router.
    path("", include(router.urls)),
]