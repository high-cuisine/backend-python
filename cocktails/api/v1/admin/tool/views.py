import django_filters
from rest_framework import viewsets, mixins

from api.base.permissions import IsActiveUser
from api.v1.admin.tool.filters import ToolFilter
from api.v1.admin.tool.serializers import AdminToolSerializer
from api.v1.admin.tool.tool_permission import ToolPermission
from apps.recipe.models import Tool
from base.pagination import BasePagination


class AdminToolViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Tool.objects.all()
    serializer_class = AdminToolSerializer
    permission_classes = [IsActiveUser, ToolPermission]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = ToolFilter
    pagination_class = BasePagination
