from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.response import Response
from .serializers import *
from api.base.permissions import IsManager, IsActiveUser
from api.v1.common import swagger
from api.v1.common.serializers import *
from apps.common.models import *


class ImageUploadView(APIView):
    parser_classes = (MultiPartParser, FileUploadParser)
    http_method_names = ['post']
    permission_classes = [IsManager]

    @swagger_auto_schema(**swagger.image_upload)
    def post(self, request, *args, **kwargs):
        serializer = ImageUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(dict(url=serializer.url))


class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FileUploadParser)
    http_method_names = ['post']
    permission_classes = [IsManager]

    @swagger_auto_schema(**swagger.file_upload)
    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(dict(url=serializer.url))


class ConfigAPIView(APIView):
    permission_classes = [IsManager]
    http_method_names = ['get']

    @swagger_auto_schema(**swagger.config_list)
    def get(self, request):
        return Response(Config.get_all())


class FAQViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [IsActiveUser]
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer

    @swagger_auto_schema(**swagger.faq_list)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class DocumentViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [IsActiveUser]
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    @swagger_auto_schema(**swagger.docs_list)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AdvertisementViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [IsActiveUser]
    queryset = Ads.objects.all()
    serializer_class = AdvertisementSerializer

    @swagger_auto_schema(**swagger.ads_list)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)