from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from api.base.permissions import IsActiveUser
from api.v1.admin.statistics.serializers import AdminStatisticsSerializer
from api.v1.admin.statistics.swagger import statistics
from apps.recipe.models import Recipe
from apps.user.models import User


class AdminStatisticsView(APIView):
    permission_classes = [IsActiveUser]

    @swagger_auto_schema(**statistics)
    def get(self, request, *args, **kwargs):
        return Response(
            data={
                'total_recipes': self.get_total_recipes(),
                'rus_recipes': self.get_rus_recipes(),
                'eng_recipes': self.get_eng_recipes(),
                'total_users': self.get_total_users(),
                'ios_users': self.get_ios_users(),
                'android_users': self.get_android_users()
            },
            status=status.HTTP_200_OK
        )

    @staticmethod
    def get_total_recipes():
        return Recipe.objects.filter(moderation_status='Approved').count()

    @staticmethod
    def get_rus_recipes():
        return Recipe.objects.filter(moderation_status='Approved', language='RUS').count()

    @staticmethod
    def get_eng_recipes():
        return Recipe.objects.filter(moderation_status='Approved', language='ENG').count()

    @staticmethod
    def get_total_users():
        return User.objects.count()

    @staticmethod
    def get_ios_users():
        return User.objects.filter(os='IOS').count()

    @staticmethod
    def get_android_users():
        return User.objects.filter(os='Android').count()
