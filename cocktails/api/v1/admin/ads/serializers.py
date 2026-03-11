from rest_framework import serializers

from apps.common.models import Ads


class AdminADSSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ads
        fields = '__all__'
