from django.db.models import Count
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.views import APIView

from api.base.permissions import IsActiveUser
from api.v1.admin.recipe.filters import RecipeFilter
from api.v1.admin.recipe.recipe_permission import RecipePermission
from api.v1.admin.recipe.serializers import AdminListRecipeSerializer, AdminUpdateRecipeSerializer, \
    AdminCreateRecipeSerializer
from api.v1.admin.recipe.swagger import recipe_create, recipe_update
from apps.recipe.models import Recipe
from base.pagination import BasePagination
from main_core import settings
from services.s3_client import S3Client

s3_client = S3Client(
    access_key=settings.AWS_ACCESS_KEY,
    secret_key=settings.AWS_SECRET_KEY
)


class AdminPendingRecipeViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Recipe.objects.filter(moderation_status='Pending').all()
    serializer_class = AdminListRecipeSerializer
    permission_classes = [IsActiveUser, RecipePermission]
    pagination_class = BasePagination
    filterset_class = RecipeFilter

    def get_queryset(self):
        queryset = super().get_queryset()

        return queryset.annotate(favorites_count=Count('favorited_by'))

    def get_serializer_class(self):
        if self.action == 'update':
            return AdminUpdateRecipeSerializer
        else:
            return AdminListRecipeSerializer

    @swagger_auto_schema(**recipe_update)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class AdminApprovedRecipeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Recipe.objects.filter(moderation_status='Approved').all()
    serializer_class = AdminListRecipeSerializer
    permission_classes = [IsActiveUser, RecipePermission]
    pagination_class = BasePagination
    filterset_class = RecipeFilter

    def get_queryset(self):
        queryset = super().get_queryset()

        return queryset.annotate(favorites_count=Count('favorited_by'))

    def get_serializer_class(self):
        if self.action == 'update':
            return AdminUpdateRecipeSerializer
        elif self.action == 'create':
            return AdminCreateRecipeSerializer
        else:
            return AdminListRecipeSerializer

    @swagger_auto_schema(**recipe_update)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(**recipe_create)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class AdminRejectedRecipeViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Recipe.objects.filter(moderation_status='Rejected').all()
    serializer_class = AdminListRecipeSerializer
    permission_classes = [IsActiveUser, RecipePermission]
    pagination_class = BasePagination
    filterset_class = RecipeFilter

    def get_queryset(self):
        queryset = super().get_queryset()

        return queryset.annotate(favorites_count=Count('favorited_by'))

    def get_serializer_class(self):
        if self.action == 'update':
            return AdminUpdateRecipeSerializer
        else:
            return AdminListRecipeSerializer

    @swagger_auto_schema(**recipe_update)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class AdminUploadUrlView(APIView):
    permission_classes = [IsActiveUser]

    def get(self, request, *args, **kwargs):
        s3_key = request.query_params.get('s3_key')
        if not s3_key:
            return Response(status=404, data={'message': 's3_key is required'})

        presigned_url = s3_client.get_presigned_url(settings.AWS_BUCKET_NAME, s3_key)

        return Response(
            data={'upload_url': presigned_url}, status=200
        )


class AdminDeleteObjectView(APIView):
    permission_classes = [IsActiveUser]

    def delete(self, request, *args, **kwargs):
        s3_key = kwargs.get('s3_key')

        if not s3_key:
            return Response(
                {'error': 's3_key is required'},
                status=400
            )

        s3_client.delete_object(settings.AWS_BUCKET_NAME, s3_key)
        return Response(
            {'success': True, 'message': f'Object {s3_key} deleted successfully'},
            status=200
        )

