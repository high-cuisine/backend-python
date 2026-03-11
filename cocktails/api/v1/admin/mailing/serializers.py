from rest_framework import serializers

from apps.common.models import Mailing


class AdminMailingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailing
        fields = '__all__'
