import django_filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets

from api.base.permissions import IsActiveUser
from api.v1.admin.ingredient.filters import IngredientFilter, IngredientCategoryFilter
from api.v1.admin.ingredient.serializers import AdminIngredientSerializer, AdminIngredientCategorySerializer, \
    AdminListIngredientCategorySectionSerializer, AdminUpdateIngredientCategorySectionSerializer
from api.v1.admin.ingredient.swagger import ingredient_category_section_update
from apps.recipe.models import Ingredient, IngredientCategory, IngredientCategorySection
from base.pagination import BasePagination


class AdminIngredientViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Ingredient.objects.all()
    serializer_class = AdminIngredientSerializer
    permission_classes = [IsActiveUser]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = BasePagination


class AdminIngredientCategoryViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = IngredientCategory.objects.all()
    serializer_class = AdminIngredientCategorySerializer
    permission_classes = [IsActiveUser]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = IngredientCategoryFilter
    pagination_class = BasePagination


class AdminIngredientCategorySectionViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = IngredientCategorySection.objects.all()
    serializer_class = AdminListIngredientCategorySectionSerializer
    permission_classes = [IsActiveUser]
    pagination_class = BasePagination

    def get_serializer_class(self):
        if self.action == 'update':
            return AdminUpdateIngredientCategorySectionSerializer
        return AdminListIngredientCategorySectionSerializer

    @swagger_auto_schema(**ingredient_category_section_update)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)



