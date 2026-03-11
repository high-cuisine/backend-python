from rest_framework import serializers
from apps.goods.models import Promo


__all__ = [
    'PromoSerializer',
    'PurchasedPromoSerializer',
    'PromoListSerializer',
    'BuyPromoSerializer',
    'PromoCodeResponseSerializer'
]

class PromoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Promo
        fields = ['id', 'name', 'description', 'cost', 'links']


class PurchasedPromoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Promo
        fields = ['id', 'name', 'code', 'description', 'cost', 'links']


class PromoListSerializer(serializers.Serializer):
    available_promos = PromoSerializer(many=True)
    purchased_promos = PurchasedPromoSerializer(many=True)


class BuyPromoSerializer(serializers.Serializer):
    promo_id = serializers.IntegerField(required=True, help_text="ID of the promo to buy")


class PromoCodeResponseSerializer(serializers.Serializer):
    promo_code = serializers.CharField(help_text="Promo code for the purchased promo")
