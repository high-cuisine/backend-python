from rest_framework import serializers
from django.db.models import Sum
from apps.user.models import *
from apps.recipe.models import *
from api.v1.recipe.serializers import RecipeDetailSerializer, ToolSerializer, RecipeIngredientSerializer
from base.tasks import send_mail
from django.utils.crypto import get_random_string

__all__ = [
    'ReferralSerializer',
    'UserSerializer',
    'FavoriteRecipeSerializer',
    'ReferralSerializer',
    'UserRecipeListSerializer',
    'UserUpdateSerializer',
    'EmailSendCodeSerializer',
    'ConfirmEmailSerializer',
    'ConfirmNewEmailSerializer',
]


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    recipe = RecipeDetailSerializer(read_only=True)

    class Meta:
        model = FavoriteRecipe
        fields = ['recipe']


class ReferralSerializer(serializers.ModelSerializer):

    class Meta:
        model = Referral
        fields = ['code']


class UserSerializer(serializers.ModelSerializer):
    points = serializers.SerializerMethodField()
    favorite_recipes_count = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = '__all__'

    def get_favorite_recipes_count(self, obj):
        return obj.favorite_recipes.count()

    def get_recipes_count(self, obj):
        return obj.recipes_user.count()

    def get_points(self, obj):
        total_points = obj.points.filter(charge=False).aggregate(total_points=Sum('points'))['total_points'] or 0
        charged_points = obj.points.filter(charge=True).aggregate(total_charged=Sum('points'))['total_charged'] or 0
        return total_points - charged_points


class UserUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    gender = serializers.CharField(required=False)
    date_of_birth = serializers.DateField(required=False)
    avatar = serializers.FileField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'gender', 'date_of_birth', 'avatar']


class UserRecipeListSerializer(serializers.ModelSerializer):
    ingredient_count = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    tools = ToolSerializer(many=True)
    is_favorite = serializers.SerializerMethodField()
    image = serializers.ImageField(source='photo', allow_null=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "ingredients",
            "ingredient_count",
            "title",
            "description",
            "instruction",
            "photo",
            "image",
            "video_url",
            "is_favorite",
            "moderation_status",
            "isEnabled",
            "user",
            "tools",
            'video_aws_key'
        ]

    def get_is_favorite(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(user=user, recipe=obj).exists()

    def get_ingredient_count(self, obj):
        return obj.recipe_ingredients.count()

    def get_ingredients(self, obj):
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(recipe_ingredients, many=True).data


class ConfirmEmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField()
    code = serializers.CharField(max_length=4, write_only=True)

    def validate(self, attrs: dict):
        user = self.context.get('user')
        email = user.email
        try:
            TempCode.objects.get(email=email, verification_code=attrs['code'])
        except TempCode.DoesNotExist:
            raise serializers.ValidationError(dict(code=['Неверный код']))

        self.user = User.objects.get(email=email)
        return attrs

    def save(self):
        user = self.context.get('user')
        email = user.email
        self.user.email = self.validated_data['new_email']
        self.user.save()
        TempCode.objects.filter(email=email).delete()


def get_verification_code():
    verification_code = get_random_string(length=4, allowed_chars='0123456789')
    return verification_code


class ConfirmNewEmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField()
    code = serializers.CharField(max_length=4, write_only=True)

    def validate(self, attrs: dict):
        user = self.context.get('user')
        email = user.email
        try:
            TempCode.objects.get(email=email, verification_code=attrs['code'])
        except TempCode.DoesNotExist:
            raise serializers.ValidationError(dict(code=['Неверный код']))

        self.user = User.objects.get(email=email)
        return attrs

    def save(self):
        user = self.context.get('user')
        email = user.email
        # self.user.email = self.validated_data['new_email']
        # self.user.save()

        verification_code = get_verification_code()
        self.send_verification_email(self.validated_data['new_email'], verification_code)

        temp_code = TempCode.objects.filter(email=email)
        temp_code.verified = True
        temp_code.save()

    def send_verification_email(self, email, verification_code):
        send_mail(
            subject="Verification Code",
            template_name="mail/password.html",
            context={"code": verification_code},
            to_email=[email]
        )


class ConfirmNewEmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField()
    code = serializers.CharField(max_length=4, write_only=True)

    def validate(self, attrs: dict):
        user = self.context.get('user')
        email = user.email
        try:
            TempCode.objects.get(email=attrs['new_email'], verification_code=attrs['code'])
        except TempCode.DoesNotExist:
            raise serializers.ValidationError(dict(code=['Неверный код']))

        try:
            TempCode.objects.get(email=email, verified=True)
        except TempCode.DoesNotExist:
            raise serializers.ValidationError(dict(code=['Требуется подтвердить старую почту']))

        self.user = User.objects.get(email=email)
        return attrs

    def save(self):
        user = self.context.get('user')
        email = user.email
        self.user.email = self.validated_data['new_email']
        self.user.save()
        TempCode.objects.filter(email=self.validated_data['new_email']).delete()
        TempCode.objects.filter(email=email).delete()


class EmailSendCodeSerializer(serializers.Serializer):
    def create(self, validated_data):
        user = self.context.get('user')
        email = user.email

        verification_code = get_verification_code()

        temporary_user, _ = TempCode.objects.get_or_create(email=email)
        temporary_user.verification_code = verification_code
        temporary_user.save()

        self.send_verification_email(email, verification_code)
        return temporary_user

    def send_verification_email(self, email, verification_code):
        send_mail(
            subject="Verification Code",
            template_name="mail/password.html",
            context={"code": verification_code},
            to_email=[email]
        )