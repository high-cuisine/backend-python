import django_filters
from django.db.models import Q
from django_filters import rest_framework as filters

from apps.recipe.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    ordering = filters.OrderingFilter(
        fields=(
            ('title', 'title'),
            ('id', 'id'),
            ('video_url', 'video_url'),
            ('favorites_count', 'favorites_count'),
            ('is_alcoholic', 'is_alcoholic'),
            ('language', 'language'),
        ),
        field_labels={
            'title': 'Recipe title',
            'id': 'Recipe ID',
            'video_url': 'Video exists',
            'favorites_count': 'Recipe Favorites count',
            'is_alcoholic': 'Alcoholic or not',
            'language': 'Recipe language',
        }
    )

    class Meta:
        model = Recipe
        fields = []

    @staticmethod
    def filter_search(queryset, name, value):
        if not value:
            return queryset

        value_list = value.split()
        q = Q()

        if value.isdigit():
            q |= Q(id=value)

        for word in value_list:
            q |= Q(title__icontains=word) | Q(recipe_ingredients__ingredient__name__icontains=word)

        if len(value_list) > 1:
            for i in range(len(value_list)):
                for j in range(i + 1, len(value_list)):
                    q |= (
                            (Q(title__icontains=value_list[i]) & Q(title__icontains=value_list[j])) |
                            (Q(recipe_ingredients__ingredient__name__icontains=value_list[i]) & Q(
                                recipe_ingredients__ingredient__name__icontains=value_list[j]))
                    )

        return queryset.filter(q).distinct()
