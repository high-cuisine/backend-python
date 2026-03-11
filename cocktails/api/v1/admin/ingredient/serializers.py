from rest_framework import serializers

from apps.recipe.models import Ingredient, IngredientCategory, IngredientCategorySection


class IngredientCategoryPreSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientCategory
        fields = ['id', 'name']


class AdminIngredientSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Ingredient
        fields = '__all__'


class AdminIngredientCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientCategory
        fields = '__all__'


class AdminListIngredientCategorySectionSerializer(serializers.ModelSerializer):
    categories = IngredientCategoryPreSerializer(many=True)

    class Meta:
        model = IngredientCategorySection
        fields = '__all__'
        read_only_fields = ['name', 'language']


class AdminUpdateIngredientCategorySectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientCategorySection
        fields = ['categories']
