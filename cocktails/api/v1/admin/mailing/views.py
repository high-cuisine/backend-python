import django_filters
from rest_framework import mixins
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.viewsets import GenericViewSet

from api.base.permissions import IsActiveUser
from api.v1.admin.mailing.filters import MailingFilter
from api.v1.admin.mailing.serializers import AdminMailingSerializer
from apps.common.models import Mailing
from base.pagination import BasePagination


class AdminMailingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    queryset = Mailing.objects.all()
    serializer_class = AdminMailingSerializer
    pagination_class = BasePagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = MailingFilter
    permission_classes = [IsActiveUser, DjangoModelPermissions]
