from rest_framework import viewsets
from assets.models import DataSource, DataRepository, Folder, File
from assets.serializers import (
    DataRepositorySerializer,
    DataSourceSerializer,
    FolderSerializer,
    FileSerializer,
)


class DataSourceViewset(viewsets.ModelViewSet):
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer


class DataRepositoryViewset(viewsets.ModelViewSet):
    queryset = DataRepository.objects.all()
    serializer_class = DataRepositorySerializer


class FolderViewset(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer


class FileViewset(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
