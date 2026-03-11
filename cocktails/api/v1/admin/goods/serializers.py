from rest_framework import serializers
from apps.goods.models import Goods


__all__ = [
    'AdminGoodsSerializer',
]


class AdminGoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = '__all__'
