from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from .serializers import GoogleSocialAuthSerializer, FacebookSocialAuthSerializer
from rest_framework.permissions import AllowAny
from .swagger import google_in, facebook_in


class GoogleSocialAuthView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = GoogleSocialAuthSerializer

    @swagger_auto_schema(**google_in)
    def post(self, request):
        """

        POST with "auth_token"

        Send an idtoken as from google to get user information

        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return Response(data, status=status.HTTP_200_OK)


class FacebookSocialAuthView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = FacebookSocialAuthSerializer

    @swagger_auto_schema(**facebook_in)
    def post(self, request):
        """

        POST with "auth_token"

        Send an access token as from facebook to get user information

        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return Response(data, status=status.HTTP_200_OK)


# class TwitterSocialAuthView(GenericAPIView):
#     serializer_class = TwitterAuthSerializer
#
#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         return Response(serializer.validated_data, status=status.HTTP_200_OK)