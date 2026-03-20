from django.db.models import Q, BooleanField, Case, When, Value, Count
from django_filters import rest_framework as filters
from django.contrib.postgres.fields import JSONField
from django.db.models import Exists, OuterRef
from apps.recipe.models import Recipe


class RecipeFilterSet(filters.FilterSet):
    q = filters.CharFilter(method='filter_q')
    ingredients = filters.CharFilter(method='filter_ingredients')
    tools = filters.CharFilter(method='filter_tools')
    alc = filters.BooleanFilter(method='filter_alc')
    ordering = filters.OrderingFilter(
        fields=(
            ('title', 'title'),
            ('video_url', 'video_url'),
            ('popularity', 'popularity'),
        ),
        field_labels={
            'title': 'Recipe title',
            'video_url': 'Video exists',
            'popularity': 'Popularity',
        }
    )

    @staticmethod
    def filter_q(queryset, name, value):
        """
        Enhanced search filter for recipes supporting:
        - Recipe title search (existing)
        - Recipe description search (NEW)
        - Recipe instruction search - searches within JSON instruction content (NEW)
        - Ingredient name search (existing)
        
        For single word: searches across ALL fields with OR logic
        For multiple words: applies AND logic - each word must be found somewhere in the recipe
        
        Args:
            queryset: Recipe queryset to filter
            name: Filter parameter name (not used)
            value: Search string (can contain multiple words)
            
        Returns:
            Filtered queryset with recipes matching the search criteria
        """
        if not value:
            return queryset

        value_list = value.split()
        
        # For single word - search across title, description, instructions AND ingredients
        if len(value_list) == 1:
            word = value_list[0]
            q = (Q(title__icontains=word) |                            # Search in recipe title
                 Q(description__icontains=word) |                      # NEW: Search in recipe description  
                 Q(instruction__icontains=word) |                      # NEW: Search in instruction JSON content
                 Q(recipe_ingredients__ingredient__name__icontains=word))  # Search in ingredient names
            return queryset.filter(q).distinct()
        
        # For multiple words - each word must be found somewhere in the recipe (AND logic)
        # Each word can match in ANY of the searchable fields (OR logic per word)
        filtered_queryset = queryset
        
        for word in value_list:
            # For each word, create OR filter across all searchable fields
            word_filter = (Q(title__icontains=word) |                            # Recipe title
                          Q(description__icontains=word) |                       # NEW: Recipe description
                          Q(instruction__icontains=word) |                       # NEW: Instruction content (JSON values)  
                          Q(recipe_ingredients__ingredient__name__icontains=word))   # Ingredient names
            filtered_queryset = filtered_queryset.filter(word_filter).distinct()
        
        return filtered_queryset

    def filter_ingredients(self, queryset, name, value):
        if not value:
            return queryset

        try:
            ids = [int(v) for v in value.replace('-', ',').split(',')]
        except ValueError:
            return queryset.none()

        # OR logic: recipe must contain AT LEAST ONE specified ingredient
        return queryset.filter(
            recipe_ingredients__ingredient__id__in=ids
        ).distinct()

    def filter_tools(self, queryset, name, value):
        if not value:
            return queryset

        try:
            ids = [int(v) for v in value.replace('-', ',').split(',')]
        except ValueError:
            return queryset.none()

        return queryset.filter(tools__id__in=ids).distinct()

    def get_queryset(self):
        queryset = super().get_queryset()

        return queryset

    def filter_alc(self, queryset, name, value):
        if value is True:
            # Рецепты с хотя бы одним алкогольным ингредиентом
            queryset = queryset.filter(is_alcoholic=True)

        elif value is False:
            # Рецепты без алкогольных ингредиентов
            queryset = queryset.filter(is_alcoholic=False)

        return queryset

    class Meta:
        model = Recipe
        fields = ['q', 'ingredients', 'tools', 'alc', 'ordering']
