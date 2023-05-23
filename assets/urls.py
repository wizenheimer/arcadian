from django.urls import path, include
from rest_framework.routers import DefaultRouter
from assets.views import (
    DataSourceViewset,
    DataRepositoryViewset,
    FolderViewset,
    FileViewset,
)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(
    r"source",
    DataSourceViewset,
    basename="source",
)
router.register(
    r"repository",
    DataRepositoryViewset,
    basename="repository",
)
router.register(
    r"files",
    FileViewset,
    basename="files",
)
router.register(
    r"folders",
    FolderViewset,
    basename="folders",
)


urlpatterns = [
    # The API URLs are now determined automatically by the router.
    path("", include(router.urls)),
]
