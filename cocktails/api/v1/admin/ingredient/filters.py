import django_filters
from django.db.models import Q
from django_filters import rest_framework as filters

from apps.recipe.models import Ingredient, IngredientCategory


class IngredientFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    ordering = filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('description', 'description'),
            ('language', 'language'),
            ('id', 'id'),
        ),
        field_labels={
            'name': 'Ingredient name',
            'description': 'Ingredient description',
            'language': 'Ingredient language',
            'id': 'Ingredient id',
        }
    )

    class Meta:
        model = Ingredient
        fields = []

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset

        query = Q()

        query |= Q(name__icontains=value)

        query |= Q(description__icontains=value)

        if value.isdigit():
            query |= Q(id=value)

        return queryset.filter(query)


class IngredientCategoryFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    ordering = filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('language', 'language'),
            ('id', 'id'),
        ),
        field_labels={
            'name': 'Ingredient category name',
            'language': 'Ingredient category language',
            'id': 'Ingredient category id',
        }
    )

    class Meta:
        model = IngredientCategory
        fields = []

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset

        query = Q()

        query |= Q(name__icontains=value)

        if value.isdigit():
            query |= Q(id=value)

        return queryset.filter(query)

