import django_filters
from rest_framework import mixins
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.viewsets import GenericViewSet

from api.base.permissions import IsActiveUser
from api.v1.admin.faq.faq_permission import FAQPermission
from api.v1.admin.faq.filters import FAQFilter
from api.v1.admin.faq.serializers import AdminFAQSerializer
from apps.common.models import FAQ
from base.pagination import BasePagination


class AdminFAQViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    queryset = FAQ.objects.all()
    serializer_class = AdminFAQSerializer
    pagination_class = BasePagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = FAQFilter
    permission_classes = [IsActiveUser, FAQPermission]
