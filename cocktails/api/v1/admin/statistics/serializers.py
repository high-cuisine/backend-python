from rest_framework import serializers

from apps.recipe.models import Recipe
from apps.user.models import User


class AdminStatisticsSerializer(serializers.Serializer):
    total_recipes = serializers.SerializerMethodField(read_only=True)
    rus_recipes = serializers.SerializerMethodField(read_only=True)
    eng_recipes = serializers.SerializerMethodField(read_only=True)
    total_users = serializers.SerializerMethodField(read_only=True)
    ios_users = serializers.SerializerMethodField(read_only=True)
    android_users = serializers.SerializerMethodField(read_only=True)

    def get_total_recipes(self, obj):
        return Recipe.objects.filter(moderation_status='Approved').count()

    def get_rus_recipes(self, obj):
        return Recipe.objects.filter(moderation_status='Approved', language='RUS').count()

    def get_eng_recipes(self, obj):
        return Recipe.objects.filter(moderation_status='Approved', language='ENG').count()

    def get_total_users(self, obj):
        return User.objects.count()

    def get_ios_users(self, obj):
        return User.objects.filter(os='IOS').count()

    def get_android_users(self, obj):
        return User.objects.filter(os='Android').count()
