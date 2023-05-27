from rest_framework import viewsets, parsers
from assets.models import DataSource, DataRepository, Folder, File
from assets.serializers import (
    VerboseDataRepositorySerializer,
    BaseDataRepositorySerializer,
    DataSourceSerializer,
    BaseFolderSerializer,
    VerboseFolderSerializer,
    BaseFileSerializer,
    VerboseFileSerializer,
)


class DataSourceViewset(viewsets.ModelViewSet):
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer


class DataRepositoryViewset(viewsets.ModelViewSet):
    queryset = DataRepository.objects.all()
    serializer_class = BaseDataRepositorySerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return VerboseDataRepositorySerializer

        if self.request.GET.get("verbose", "false") == "false":
            return BaseDataRepositorySerializer
        else:
            return VerboseDataRepositorySerializer


class FolderViewset(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = BaseFolderSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return VerboseFolderSerializer

        if self.request.GET.get("verbose", "false") == "false":
            return BaseFolderSerializer
        else:
            return VerboseFolderSerializer


class FileViewset(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = BaseFileSerializer
    parser_classes = [
        parsers.MultiPartParser,
        parsers.FormParser,
    ]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return VerboseFileSerializer

        if self.request.GET.get("verbose", "false") == "false":
            return BaseFileSerializer
        else:
            return VerboseFileSerializer
