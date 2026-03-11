from apps.user.models import User, Referral
from apps.recipe.models import FavoriteRecipe, Recipe
from rest_framework.exceptions import NotAuthenticated
from .serializers import *
from .swagger import get_referral, recipe_pending, email_verification, confirm_email, confirm_new_email
import random
import string
from api.base.permissions import IsActiveUser
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.generics import GenericAPIView
from rest_framework import mixins
from api.v1.recipe.serializers import RecipeListSerializer
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from api.v1.recipe.serializers import RecipeDetailSerializer
from .filters import UserRecipeFilterSet


class UserRecipeViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    serializer_class = UserRecipeListSerializer
    permission_classes = [IsActiveUser]
    filterset_class = UserRecipeFilterSet

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Recipe.objects.none()
        if not self.request.user.is_authenticated:
            raise NotAuthenticated("User is not authenticated")
        return Recipe.objects.filter(user=self.request.user)

    @swagger_auto_schema(**recipe_pending)
    @action(methods=['get'], detail=True)
    def pending(self, request, pk=None):
        recipe = Recipe.objects.get(pk=pk)
        recipe.moderation_status = 'Pending'
        recipe.save()
        serializer = RecipeDetailSerializer(recipe, context={'request': request})
        return Response(serializer.data)


class FavoriteUserRecipeViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, GenericViewSet):
    serializer_class = FavoriteRecipeSerializer
    permission_classes = [IsActiveUser]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return FavoriteRecipe.objects.none()
        if self.request.user.is_anonymous:
            raise NotAuthenticated("User is not authenticated")
        return FavoriteRecipe.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        favorite_recipes = self.get_queryset()
        recipe_ids = favorite_recipes.values_list('recipe_id', flat=True)
        recipes = Recipe.objects.filter(id__in=recipe_ids)

        serializer = RecipeListSerializer(recipes, many=True, context={'request': request})

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        recipe_id = request.data.get('recipe')
        if not recipe_id:
            raise ValidationError("Recipe ID is required")

        try:
            recipe = Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            raise NotFound("Recipe not found")

        _, created = FavoriteRecipe.objects.get_or_create(user=request.user, recipe=recipe)

        if created:
            return Response({'status': 'Recipe added to favorites'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status': 'Recipe is already in favorites'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def d(self, request):
        recipe_id = request.data.get('recipe')
        try:
            favorite = FavoriteRecipe.objects.get(user=request.user, recipe_id=recipe_id)
        except FavoriteRecipe.DoesNotExist:
            raise NotFound("Recipe is not in favorites")

        favorite.delete()
        return Response({'status': 'Recipe removed from favorites'}, status=status.HTTP_204_NO_CONTENT)

class UserViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsActiveUser]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id).prefetch_related('favorite_recipes', 'recipes_user')

    def get_object(self):
        user = self.request.user
        if user.is_anonymous:
            raise NotAuthenticated("User is not authenticated")
        return user

    def get_serializer_class(self):
        if self.action == 'update':
            return UserUpdateSerializer
        return UserSerializer
    

class ReferralViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = ReferralSerializer
    permission_classes = [IsActiveUser]

    def generate_random_code(self, length=12):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for i in range(length))

    @swagger_auto_schema(**get_referral)
    def list(self, request, *args, **kwargs):
        user = self.request.user
        try:
            referral = Referral.objects.get(user=user)
        except Referral.DoesNotExist:
            referral_code = self.generate_random_code()
            referral = Referral.objects.create(user=user, code=referral_code)

        serializer = self.get_serializer(referral)
        return Response(serializer.data)


class EmailVerificationCodeView(GenericAPIView):
    serializer_class = EmailSendCodeSerializer
    permission_classes = [IsActiveUser]

    @swagger_auto_schema(**email_verification)
    def post(self, request):
        user = self.request.user
        serializer = self.get_serializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Verification code sent to email'}, status=status.HTTP_200_OK)


class ConfirmEmailView(GenericAPIView):
    serializer_class = ConfirmEmailSerializer
    permission_classes = [IsActiveUser]

    @swagger_auto_schema(**confirm_email)
    def post(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Verification code sent to new email'}, status=status.HTTP_201_CREATED)


class ConfirmNewEmailView(GenericAPIView):
    serializer_class = ConfirmEmailSerializer
    permission_classes = [IsActiveUser]

    @swagger_auto_schema(**confirm_new_email)
    def post(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Email successfully change'}, status=status.HTTP_201_CREATED)