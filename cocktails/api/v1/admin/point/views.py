import django_filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.base.permissions import IsActiveUser
from apps.common.models import Config
from apps.user.models import User
from base.pagination import BasePagination
from .filters import PointFilter
from .point_permission import PointPermission
from .serializers import AdminPointUserSerializer, AdminCreatePointUserSerializer, AdminPointConfigSerializer
from .swagger import points_create


class AdminPointViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = AdminPointUserSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = PointFilter
    pagination_class = BasePagination
    permission_classes = [IsActiveUser, PointPermission]

    @swagger_auto_schema(**points_create)
    def create(self, request, *args, **kwargs):
        serializer = AdminCreatePointUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AdminPointConfigViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    queryset = Config.objects.all()
    serializer_class = AdminPointConfigSerializer
    permission_classes = [IsActiveUser, PointPermission]
