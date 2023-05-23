from rest_framework import serializers
from assets.models import DataSource, DataRepository, Folder, File

# TODO: build hieraries from data sources


class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSource
        fields = (
            "id",
            "source",
            "key",
            "workspace",
        )


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = "__all__"


class FolderSerializer(serializers.ModelSerializer):
    files = FileSerializer(
        many=True,
        read_only=True,
    )
    subfolder = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = (
            "id",
            "name",
            "subfolder",
            "files",
        )

    def get_subfolder(self, folder):
        subfolders = Folder.objects.filter(parent=folder)
        serializer = self.__class__(subfolders, many=True)
        return serializer.data


class DataRepositorySerializer(serializers.ModelSerializer):
    folder = serializers.SerializerMethodField()

    class Meta:
        model = DataRepository
        fields = (
            "id",
            "folder",
        )

    def get_folder(self, repository):
        folder = Folder.objects.filter(repository=repository)
        serializer = FolderSerializer(folder, many=True)
        return serializer.data
