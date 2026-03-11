import django_filters
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets, status
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.views import APIView

from api.base.permissions import IsActiveUser
from api.v1.admin.promo.filters import PromoFilter, PurchasedPromoFilter
from api.v1.admin.promo.promo_permission import PromoPermission
from api.v1.admin.promo.serializers import AdminPromoSerializer, AdminPurchasedPromoSerializer
from api.v1.admin.promo.swagger import purchased_promo_get, purchased_promo_post, search, promo
from apps.goods.models import Promo, PurchasedPromo
from apps.user.models import User
from base.pagination import BasePagination


class PromoAdminViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = AdminPromoSerializer
    permission_classes = [IsActiveUser, PromoPermission]
    queryset = Promo.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = PromoFilter
    pagination_class = BasePagination


class PromoPurchasedAdminViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pagination_class = BasePagination
    permission_classes = [IsActiveUser, PromoPermission]
    filterset_class = PurchasedPromoFilter
    queryset = PurchasedPromo.objects.all()

    @swagger_auto_schema(manual_parameters=[search, promo], **purchased_promo_get)
    def list(self, request):
        promo_id = request.query_params.get('promo')

        queryset = PurchasedPromo.objects.filter(promo_id=promo_id)

        serializer = AdminPurchasedPromoSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(**purchased_promo_post)
    def create(self, request):
        user_id = request.data.get('user')
        promo_id = request.data.get('promo')

        try:
            Promo.objects.get(id=promo_id)
        except Promo.DoesNotExist:
            return Response({"error": "Promo not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if PurchasedPromo.objects.filter(user_id=user_id, promo_id=promo_id).exists():
            return Response({"error": "User already purchased this promo"}, status=status.HTTP_400_BAD_REQUEST)

        purchased_promo = PurchasedPromo.objects.create(user_id=user_id, promo_id=promo_id)
        serializer = AdminPurchasedPromoSerializer(purchased_promo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
