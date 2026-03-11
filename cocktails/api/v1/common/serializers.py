import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import serializers
from apps.common.models import *
from services.storage import StorageClient


__all__ = [
    'ImageUploadSerializer',
    'FileUploadSerializer',
    'FAQSerializer',
    'DocumentSerializer',
    'AdvertisementSerializer',
]


class ImageUploadSerializer(serializers.Serializer):
    url = None
    image_file = serializers.ImageField(read_only=False, write_only=True, required=True)
    image_name = serializers.CharField(max_length=255, read_only=False, write_only=True, required=True)
    width = serializers.IntegerField(min_value=100, read_only=False, write_only=True, required=True)
    height = serializers.IntegerField(min_value=100, read_only=False, write_only=True, required=True)

    class Meta:
        fields = ('image_file', 'image_name', 'width', 'height')

    def create(self, validated_data):
        name = validated_data['image_file'].name
        ext = name.split('.')[-1]
        path = default_storage.save(
            f'tmp/upload/{validated_data["image_name"]}.{ext}',
            ContentFile(validated_data['image_file'].read()),
        )
        tmp_file_path = os.path.join('media', path)
        storage_client = StorageClient()
        self.url = storage_client.upload_image(
            path=tmp_file_path,
            width=validated_data['width'],
            height=validated_data['height'],
        )
        return self.url


class FileUploadSerializer(serializers.Serializer):
    url = None
    file = serializers.FileField(read_only=False, write_only=True, required=True)
    name = serializers.CharField(max_length=255, read_only=False, write_only=True, required=True)

    class Meta:
        fields = ('file', 'name')

    def create(self, validated_data):
        name = validated_data['file'].name
        ext = name.split('.')[-1]
        path = default_storage.save(
            f'tmp/upload/{validated_data["name"]}.{ext}',
            ContentFile(validated_data['file'].read()),
        )
        tmp_file_path = os.path.join('media', path)
        storage_client = StorageClient()
        self.url = storage_client.upload_file(
            path=tmp_file_path,
        )
        return self.url


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'


class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ads
        fields = '__all__'
