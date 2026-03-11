from django.db.models import Sum, Q
from rest_framework import serializers

from apps.common.models import Config
from apps.user.models import Point, User

__all__ = [
    'AdminListPointSerializer',
    'AdminPointUserSerializer',
    'AdminCreatePointUserSerializer',
    'AdminPointConfigSerializer'
]


class AdminListPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = ['id', 'points', 'text', 'charge', 'created_at']


class AdminPointUserSerializer(serializers.ModelSerializer):
    points = AdminListPointSerializer(many=True, read_only=True)
    total_points = serializers.SerializerMethodField(read_only=True)

    def get_total_points(self, obj):
        aggregated = obj.points.aggregate(
            total_charged=Sum('points', filter=Q(charge=True)),
            total_points=Sum('points', filter=Q(charge=False))
        )
        total_charged = aggregated['total_charged'] or 0
        total_points = aggregated['total_points'] or 0

        return total_points - total_charged

    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'total_points', 'points']


class AdminCreatePointUserSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Point
        fields = ['user', 'text', 'points', 'charge']


class AdminPointConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = Config
        fields = ['id', 'name', 'value']
