from rest_framework import serializers
from rest_framework.fields import empty
from assets.models import DataSource, DataRepository, Folder, File

# TODO: build hieraries from data sources
# TODO: queryset optimization for folders lookup


class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSource
        fields = (
            "id",
            "source",
            "key",
            "workspace",
        )


class BaseFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = (
            "id",
            "name",
        )


class VerboseFileSerializer(BaseFileSerializer):
    class Meta(BaseFileSerializer.Meta):
        fields = "__all__"


class BaseFolderSerializer(serializers.ModelSerializer):
    file_count = serializers.SerializerMethodField()
    subfolder_count = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = (
            "id",
            "name",
            "file_count",
            "subfolder_count",
        )

    def get_file_count(self, folder):
        files = folder.files.all()
        return files.count()

    def get_subfolder_count(self, folder):
        subfolders = Folder.objects.filter(parent=folder)
        return subfolders.count()


class VerboseFolderSerializer(BaseFolderSerializer):
    files = VerboseFileSerializer(
        many=True,
        read_only=True,
    )
    subfolder = serializers.SerializerMethodField()

    class Meta(BaseFolderSerializer.Meta):
        model = Folder
        fields = BaseFolderSerializer.Meta.fields + (
            "files",
            "subfolder",
        )

    def get_subfolder(self, folder):
        subfolders = Folder.objects.filter(parent=folder)
        serializer = self.__class__(subfolders, many=True)
        return serializer.data


class BaseDataRepositorySerializer(serializers.ModelSerializer):
    total_folders = serializers.SerializerMethodField()

    class Meta:
        model = DataRepository
        fields = (
            "id",
            "total_folders",
        )

    def get_total_folders(self, repository):
        folder = Folder.objects.filter(repository=repository)
        return folder.count()


class VerboseDataRepositorySerializer(BaseDataRepositorySerializer):
    folder = serializers.SerializerMethodField()

    class Meta(BaseDataRepositorySerializer.Meta):
        model = DataRepository
        fields = BaseDataRepositorySerializer.Meta.fields + ("folder",)

    def get_folder(self, repository):
        folder = Folder.objects.filter(repository=repository)
        serializer = VerboseFolderSerializer(folder, many=True)
        return serializer.data
