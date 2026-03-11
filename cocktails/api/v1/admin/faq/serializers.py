from rest_framework import serializers

from apps.common.models import FAQ


class AdminFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'
