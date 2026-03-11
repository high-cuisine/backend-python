from rest_framework import serializers
from apps.goods.models import Goods


__all__ = [
    'GoodsSerializer',
]


class GoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = ['id', 'name', 'description', 'price', 'photo', 'link']
