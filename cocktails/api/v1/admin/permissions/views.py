from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.admin.permissions.serializers import AdminPermissionSerializer
from apps.channel.models import Ticket
from apps.common.models import Mailing, Ads, FAQ, Config
from apps.goods.models import Promo, PurchasedPromo
from apps.user.models import User, Point, Referral


class AdminPermissionsView(APIView):
    def get(self, request, *args, **kwargs):
        user_content_type = ContentType.objects.get_for_model(User)
        mailing_content_type = ContentType.objects.get_for_model(Mailing)
        ads_content_type = ContentType.objects.get_for_model(Ads)
        faq_content_type = ContentType.objects.get_for_model(FAQ)
        promo_content_type = ContentType.objects.get_for_model(Promo)
        purchased_promo_content_type = ContentType.objects.get_for_model(PurchasedPromo)
        referral_content_type = ContentType.objects.get_for_model(Referral)
        points_content_type = ContentType.objects.get_for_model(Point)
        tickets_content_type = ContentType.objects.get_for_model(Ticket)
        config_content_type = ContentType.objects.get_for_model(Config)

        permissions = Permission.objects.filter(
            content_type__in=[
                user_content_type,
                mailing_content_type,
                ads_content_type,
                points_content_type,
                referral_content_type,
                tickets_content_type,
                promo_content_type,
                faq_content_type,
                purchased_promo_content_type,
                config_content_type,
            ]
        ).select_related('content_type')

        serializer = AdminPermissionSerializer(permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
