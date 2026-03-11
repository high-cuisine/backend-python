import json
from rest_framework import serializers
from apps.recipe.models import *
from apps.reaction.models import Claim
from apps.recipe.models import FavoriteRecipe
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from apps.recipe.utils import convert_google_drive_url

__all__ = [
    'SelectionRecipeSerializer',
    'IngredientCategorySerializer',
    'IngredientCategorySectionSerializer',
    'IngredientSerializer',
    'ViewToolSerializer',
    'ToolSerializer',
    'UpdateRecipeSerializer',
    'ListRecipeIngredientSerializer',
    'RecipeIngredientSerializer',
    'CreateRecipeSerializer',
    'RecipeDetailSerializer',
    'RecipeListSerializer',
    'ClaimSerializer',
]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'name', 'quantity', 'type']

    def get_name(self, obj):
        return obj.ingredient.name


class ListRecipeIngredientSerializer(serializers.ModelSerializer):
    name = serializers.IntegerField(source='ingredient.name')
    count = serializers.CharField(source='quantity')
    type = serializers.CharField()

    class Meta:
        model = RecipeIngredient
        fields = ['name', 'count', 'type']


class SelectionRecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    missing_ingredients = serializers.SerializerMethodField()
    missing_ingredients_count = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            "id",
            "ingredients",
            "title",
            "description",
            "instruction",
            "photo",
            "video_url",
            "user",
            "tools",
            "missing_ingredients",
            "missing_ingredients_count",
        ]

    def get_ingredients(self, obj):
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(recipe_ingredients, many=True).data

    def get_missing_ingredients(self, obj):
        return getattr(obj, 'missing_ingredients', [])

    def get_missing_ingredients_count(self, obj):
        return getattr(obj, 'missing_ingredients_count', 0)


class IngredientSerializer(serializers.ModelSerializer):
    recipes_count = serializers.SerializerMethodField()
    has_recipes = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'description', 'category', 'is_alcoholic', 'recipes_count', 'has_recipes']

    def get_recipes_count(self, obj):
        return getattr(obj, 'recipes_count', None)

    def get_has_recipes(self, obj):
        value = getattr(obj, 'has_recipes', None)
        if value is None:
            # Fallback: if recipes_count provided, infer boolean
            count = getattr(obj, 'recipes_count', None)
            if count is not None:
                return count > 0
        return value


class IngredientCategorySerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta:
        model = IngredientCategory
        fields = ['id', 'name', 'ingredients', 'is_main', 'is_alcoholic']


class IngredientCategorySectionSerializer(serializers.ModelSerializer):
    categories = IngredientCategorySerializer(many=True, read_only=True)

    class Meta:
        model = IngredientCategorySection
        fields = ['id', 'name', 'categories']


class ViewToolSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = Tool
        fields = ['id', 'name', 'description', 'history', 'how_to_use', 'recipes', 'photo', 'links']

    def get_recipes(self, obj):
        return [recipe.title for recipe in obj.recipes_tool.all()]


class ToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = '__all__'


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(source='recipe_ingredients', many=True)
    tools = serializers.PrimaryKeyRelatedField(queryset=Tool.objects.all(), many=True, write_only=True)
    is_alcoholic = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            "id",
            "ingredients",
            "title",
            "description",
            "instruction",
            "photo",
            "video_url",
            "user",
            "tools",
            'is_alcoholic',
            'video_aws_key'
        ]

    def get_is_alcoholic(self, obj):
        pass

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients', [])
        tools_data = validated_data.pop('tools', [])

        is_alcoholic = any(
            ingredient_data['ingredient'].is_alcoholic
            for ingredient_data in ingredients_data
            if ingredient_data.get('ingredient')
        )

        with transaction.atomic():
            recipe = Recipe.objects.create(**validated_data, is_alcoholic=is_alcoholic)

            for ingredient_data in ingredients_data:
                ingredient = ingredient_data['ingredient']
                if not ingredient:
                    raise serializers.ValidationError(f"Ingredient with id {ingredient} does not exist.")
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    quantity=ingredient_data['quantity'],
                    type=ingredient_data['type']
                )

            if tools_data:
                recipe.tools.set(tools_data)

        return recipe


class UpdateRecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(source='recipe_ingredients', many=True)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "ingredients",
            "title",
            "description",
            "instruction",
            "photo",
            "video_url",
            "user",
            "tools",
        ]

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients')
        instance = super().update(instance, validated_data)

        instance.recipe_ingredients.all().delete()

        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient_id=ingredient_data['ingredient']['id'],
                quantity=ingredient_data['quantity'],
                type=ingredient_data['type']
            )

        return instance


class RecipeDetailSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)
    tools = ToolSerializer(many=True)
    user = serializers.StringRelatedField()
    is_favorite = serializers.SerializerMethodField()
    claimed = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            "id",
            "ingredients",
            "title",
            "description",
            "instruction",
            "photo",
            "photo_url",
            "external_photo_url",
            "video_url",
            "is_favorite",
            "claimed",
            "user",
            "tools",
            'video_aws_key'
        ]

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request is None:
            raise KeyError('request')
        user = request.user
        if user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(user=user, recipe=obj).exists()

    def get_claimed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Claim.objects.filter(content_type=ContentType.objects.get_for_model(obj),
                                    object_id=obj.id,
                                    user=request.user).exists()

    def get_photo_url(self, obj):
        """
        Return the appropriate photo URL: external_photo_url if exists, 
        otherwise local photo.url, or None if neither exists.
        Automatically converts Google Drive URLs to direct image URLs.
        """
        # Priority: external URL first, then local file
        if obj.external_photo_url:
            return convert_google_drive_url(obj.external_photo_url)
        
        if obj.photo:
            # Check if photo field contains external URL (legacy data)
            photo_str = str(obj.photo)
            if photo_str.startswith(('http://', 'https://')) or 'http%3A' in photo_str or 'https%3A' in photo_str:
                return convert_google_drive_url(photo_str)
            else:
                # Normal local file - return full URL
                try:
                    request = self.context.get('request')
                    if request:
                        return request.build_absolute_uri(obj.photo.url)
                    return obj.photo.url
                except (ValueError, AttributeError):
                    return None
        
        return None


class RecipeListSerializer(serializers.ModelSerializer):
    ingredient_count = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    tools = ToolSerializer(many=True)
    is_favorite = serializers.SerializerMethodField()
    image = serializers.ImageField(source='photo', allow_null=True, required=False)
    claimed = serializers.SerializerMethodField()
    missing_ingredients = serializers.SerializerMethodField()
    missing_ingredients_count = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()

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
            "photo_url",
            "external_photo_url",
            "video_url",
            "is_favorite",
            "claimed",
            "user",
            "tools",
            "missing_ingredients",
            "missing_ingredients_count",
            "is_alcoholic",
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

    def get_claimed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Claim.objects.filter(content_type=ContentType.objects.get_for_model(obj),
                                    object_id=obj.id,
                                    user=user).exists()

    def get_missing_ingredients(self, obj):
        request = self.context.get('request')
        ingredient_ids = request.query_params.get('ingredients', '') if request else ''
        try:
            ingredient_ids = [int(v) for v in ingredient_ids.replace('-', ',').split(',') if v]
        except ValueError:
            ingredient_ids = []

        if not ingredient_ids:
            return []

        missing_ingredient_ids = set(ingredient_ids) - set(
            obj.recipe_ingredients.filter(ingredient__id__in=ingredient_ids)
            .values_list('ingredient_id', flat=True)
        )
        missing_ingredients = Ingredient.objects.filter(id__in=missing_ingredient_ids)
        return IngredientSerializer(missing_ingredients, many=True).data

    def get_missing_ingredients_count(self, obj):
        request = self.context.get('request')
        ingredient_ids = request.query_params.get('ingredients', '') if request else ''
        try:
            ingredient_ids = [int(v) for v in ingredient_ids.replace('-', ',').split(',') if v]
        except ValueError:
            ingredient_ids = []

        if not ingredient_ids:
            return 0

        missing_ingredient_ids = set(ingredient_ids) - set(
            obj.recipe_ingredients.filter(ingredient__id__in=ingredient_ids)
            .values_list('ingredient_id', flat=True)
        )
        return len(missing_ingredient_ids)

    def get_photo_url(self, obj):
        """
        Return the appropriate photo URL: external_photo_url if exists, 
        otherwise local photo.url, or None if neither exists.
        Automatically converts Google Drive URLs to direct image URLs.
        """
        # Priority: external URL first, then local file
        if obj.external_photo_url:
            return convert_google_drive_url(obj.external_photo_url)
        
        if obj.photo:
            # Check if photo field contains external URL (legacy data)
            photo_str = str(obj.photo)
            if photo_str.startswith(('http://', 'https://')) or 'http%3A' in photo_str or 'https%3A' in photo_str:
                return convert_google_drive_url(photo_str)
            else:
                # Normal local file - return full URL
                try:
                    request = self.context.get('request')
                    if request:
                        return request.build_absolute_uri(obj.photo.url)
                    return obj.photo.url
                except (ValueError, AttributeError):
                    return None
        
        return None


class ClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
        fields = ['id', 'user', 'content_type', 'object_id', 'created_at']
        read_only_fields = ['user', 'content_type', 'object_id', 'created_at']
