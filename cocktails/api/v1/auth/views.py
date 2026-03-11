from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from apps.user.models import TempCode
from rest_framework.permissions import AllowAny
from api.v1.auth import swagger
from api.v1.auth.serializers import *
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token

import logging

logger = logging.getLogger(__name__)


class EmailVerificationRequestView(GenericAPIView):
    serializer_class = EmailVerificationRequestSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(**swagger.email_verification_request)
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Verification code sent to email'}, status=status.HTTP_200_OK)


class CodeVerificationView(GenericAPIView):
    serializer_class = CodeVerificationSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(**swagger.code_verification)
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'detail': 'Email verified successfully'}, status=status.HTTP_200_OK)


class UserRegistrationView(GenericAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(**swagger.user_registration)
    def post(self, request):
        email = request.data.get('email')
        temporary_user = get_object_or_404(TempCode, email=email)
        serializer = self.get_serializer(data=request.data, context={'email': email})
        serializer.is_valid(raise_exception=True)
        _, token = serializer.save()
        temporary_user.delete()
        return Response(
            {'detail': 'User registered successfully', 'token': token.key},
            status=status.HTTP_201_CREATED
        )


class WebSignInView(GenericAPIView):
    serializer_class = WebSignInRequestSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(**swagger.web_sign_in)
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token, _ = Token.objects.get_or_create(user=serializer.user)
        response_serializer = WebSignInResponseSerializer(instance=serializer.user, context={'token': token.key})
        return Response(response_serializer.data)


class ResetPasswordView(GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(**swagger.reset_password)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Verification code sent to email'}, status=status.HTTP_200_OK)


class ConfirmResetCodeView(GenericAPIView):
    serializer_class = ConfirmResetCodeSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(**swagger.confirm_reset_code)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'detail': 'Code verified successfully'}, status=status.HTTP_200_OK)


class ConfirmPasswordView(GenericAPIView):
    serializer_class = ConfirmPasswordSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(**swagger.confirm_password)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Password reset successfully'}, status=status.HTTP_201_CREATED)
