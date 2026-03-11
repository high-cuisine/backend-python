from rest_framework import serializers

from apps.recipe.models import Tool


class AdminToolSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tool
        fields = '__all__'
