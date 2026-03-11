from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from base.pagination import BasePagination
from rest_framework.permissions import AllowAny
from apps.goods.models import Goods
from drf_yasg.utils import swagger_auto_schema
from .serializers import AdminGoodsSerializer


class GoodsViewSet(mixins.ListModelMixin, mixins.DestroyModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = Goods.objects.all()
    serializer_class = AdminGoodsSerializer
    permission_classes = [AllowAny]
    pagination_class = BasePagination

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)