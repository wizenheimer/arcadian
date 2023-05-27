from rest_framework import serializers
from django.core.exceptions import ValidationError
from assets.validators import validate_api_key
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

    def validate(self, attrs):
        source = attrs.get("source", None)
        if source is not "Self Reported":
            key = attrs.get("key", None)
            if not validate_api_key(api_key=key, agent="stripe"):
                raise ValidationError("The API key is invalid or unauthorized")
        return super().validate(attrs)


class BaseFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = (
            "id",
            "name",
            "content",
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
    tags = serializers.SerializerMethodField()
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

    def get_tags(self, folder):
        tags = folder.tags.all()
        return tags.values("title")


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
