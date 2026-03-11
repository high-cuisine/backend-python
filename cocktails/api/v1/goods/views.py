from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from base.pagination import BasePagination
from rest_framework.permissions import AllowAny
from .swagger import goods_list, goods_retrieve
from .serializers import GoodsSerializer
from apps.goods.models import Goods
from drf_yasg.utils import swagger_auto_schema
from .filters import GoodsFilterSet


class GoodsViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer
    permission_classes = [AllowAny]
    pagination_class = BasePagination
    filterset_class = GoodsFilterSet

    @swagger_auto_schema(**goods_list)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(**goods_retrieve)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)