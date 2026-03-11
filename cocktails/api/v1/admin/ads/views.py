import django_filters
from rest_framework import mixins
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.viewsets import GenericViewSet

from api.base.permissions import IsActiveUser
from api.v1.admin.ads.ads_permission import ADSPermission
from api.v1.admin.ads.filters import ADSFilter
from api.v1.admin.ads.serializers import AdminADSSerializer
from apps.common.models import Ads
from base.pagination import BasePagination


class AdminADSViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    queryset = Ads.objects.all()
    serializer_class = AdminADSSerializer
    pagination_class = BasePagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = ADSFilter
    permission_classes = [IsActiveUser, ADSPermission]
