import django_filters
from django_filters import rest_framework as filters
from django.db.models import Q

from apps.user.models import Point, User


class PointFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    ordering = filters.OrderingFilter(
        fields=(
            ('email', 'email'),
            ('id', 'id'),
        ),
        field_labels={
            'email': 'User email',
            'id': 'User ID',
        }
    )

    class Meta:
        model = User
        fields = []

    def filter_search(self, queryset, name, value):
        query = Q()

        if any(char.isdigit() for char in value):
            query |= Q(phone__icontains=value)

        query |= Q(email__icontains=value)

        if value.isdigit():
            query |= Q(id=value)

        return queryset.filter(query)

