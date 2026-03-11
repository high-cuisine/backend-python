from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from api.v1.admin.auth.serializers import AdminWebSignInRequestSerializer, AdminRegisterUserSerializer

import logging

logger = logging.getLogger(__name__)


class AdminWebSignInView(GenericAPIView):
    serializer_class = AdminWebSignInRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token, _ = Token.objects.get_or_create(user=serializer.user)

        user_data = AdminRegisterUserSerializer(serializer.user).data

        return Response({
            'token': token.key,
            'user': user_data
        })