from rest_framework import serializers

from apps.goods.models import Promo, PurchasedPromo
from apps.user.models import User


class AdminPurchasedPromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasedPromo
        fields = '__all__'


class AdminPromoSerializer(serializers.ModelSerializer):
    how_much_purchased = serializers.SerializerMethodField(read_only=True)

    def get_how_much_purchased(self, obj):
        return obj.purchasedpromo_set.count()

    class Meta:
        model = Promo
        fields = ['id', 'name', 'code', 'description', 'cost', 'links', 'how_much_purchased']
