import django_filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.base.permissions import IsActiveUser
from apps.user.models import User
from base.pagination import BasePagination
from .filters import ProfileFilter
from .profile_permission import ProfilePermission
from .serializers import AdminUserSerializer, AdminUserUpdateSerializer, AdminUserCreateSerializer
from .swagger import profile_update, profile_create


class AdminUserViewSet(mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       GenericViewSet):
    serializer_class = AdminUserSerializer
    permission_classes = [IsActiveUser, ProfilePermission]
    queryset = User.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = ProfileFilter
    pagination_class = BasePagination

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = AdminUserSerializer
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(**profile_update)
    def update(self, request, *args, **kwargs):
        partial = request.data.get('partial', False)
        user = self.get_object()
        serializer = AdminUserUpdateSerializer(user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(AdminUserSerializer(user, many=False).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(**profile_create)
    def create(self, request, *args, **kwargs):
        serializer = AdminUserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(AdminUserSerializer(user, many=False).data, status=status.HTTP_201_CREATED)