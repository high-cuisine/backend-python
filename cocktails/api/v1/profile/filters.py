from django.db.models import Q, BooleanField, Case, When, Value
from django_filters import rest_framework as filters
from apps.recipe.models import Recipe


class UserRecipeFilterSet(filters.FilterSet):
    q = filters.CharFilter(method='filter_q')

    @staticmethod
    def filter_q(queryset, name, value):
        if not value:
            return queryset

        value_list = value.split()
        q = Q()

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

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    class Meta:
        model = Recipe
        fields = ['q']
