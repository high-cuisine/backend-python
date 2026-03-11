import django_filters
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions

from api.base.permissions import IsActiveUser
from api.v1.admin.referral.filters import ReferralFilter
from api.v1.admin.referral.refferal_permission import ReferralPermission
from api.v1.admin.referral.serializers import AdminReferralSerializer
from apps.user.models import Referral
from base.pagination import BasePagination


class ReferralAdminViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = AdminReferralSerializer
    permission_classes = [IsActiveUser, ReferralPermission]
    queryset = Referral.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = ReferralFilter
    pagination_class = BasePagination
