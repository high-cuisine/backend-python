import django_filters
from django_filters import rest_framework as filters
from django.db.models import Q

from apps.recipe.models import Tool


class ToolFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    ordering = filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('description', 'description'),
            ('language', 'language'),
            ('id', 'id'),
        ),
        field_labels={
            'name': 'Tool name',
            'description': 'Tool description',
            'language': 'Tool language',
            'id': 'Tool id',
        }
    )

    class Meta:
        model = Tool
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