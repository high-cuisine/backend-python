from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.permissions import AllowAny
from .swagger import promo_list, promo_retrieve, promo_buy
from .serializers import PromoSerializer, BuyPromoSerializer, PromoCodeResponseSerializer, PurchasedPromoSerializer, PromoListSerializer
from apps.goods.models import Promo, PurchasedPromo
from apps.user.models import Point
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from api.base.permissions import IsActiveUser
from django.db.models import Sum, Case, When, IntegerField, F

class PromoViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = Promo.objects.all()
    serializer_class = PromoSerializer
    permission_classes = [IsActiveUser]

    @swagger_auto_schema(**promo_list)
    def list(self, request, *args, **kwargs):
        user = request.user

        if user.is_anonymous:
            return super().list(request, *args, **kwargs)

        purchased_promo_ids = PurchasedPromo.objects.filter(user=user).values_list('promo_id', flat=True)

        available_promos = Promo.objects.exclude(id__in=purchased_promo_ids)
        purchased_promos = Promo.objects.filter(id__in=purchased_promo_ids)

        response_data = {
            "available_promos": PromoSerializer(available_promos, many=True).data,
            "purchased_promos": PurchasedPromoSerializer(purchased_promos, many=True).data
        }

        response_serializer = PromoListSerializer(data=response_data)
        response_serializer.is_valid()

        return Response(response_serializer.data)

    @swagger_auto_schema(**promo_retrieve)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(**promo_buy)
    @action(detail=False, methods=['post'])
    def buy(self, request):
        serializer = BuyPromoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        promo_id = serializer.validated_data['promo_id']
        user = request.user

        if user.is_anonymous:
            return Response({"detail": "User is anonymous."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            promo = Promo.objects.get(id=promo_id)
        except Promo.DoesNotExist:
            return Response({"detail": "Promo not found."}, status=status.HTTP_404_NOT_FOUND)

        if PurchasedPromo.objects.filter(user=user, promo=promo).exists():
            return Response({"detail": "Promo already purchased."}, status=status.HTTP_400_BAD_REQUEST)

        cost = promo.cost

        points_data = Point.objects.filter(user=user).aggregate(
            total_earned=Sum(Case(When(charge=False, then='points'), output_field=IntegerField())),
            total_spent=Sum(Case(When(charge=True, then='points'), output_field=IntegerField()))
        )

        points_available = (points_data['total_earned'] or 0) - (points_data['total_spent'] or 0)

        if points_data is None or points_available < cost:
            return Response({"detail": "Not enough points available."}, status=status.HTTP_400_BAD_REQUEST)

        Point.objects.create(
            user=user,
            points=cost,
            charge=True,
            text=f'Purchase promo {promo_id}'
        )

        PurchasedPromo.objects.create(user=user, promo=promo)

        response_serializer = PromoCodeResponseSerializer(data={"promo_code": promo.code})
        response_serializer.is_valid()

        return Response(response_serializer.data, status=status.HTTP_200_OK)