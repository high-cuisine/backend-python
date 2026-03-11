import django_filters
from django_filters import rest_framework as filters
from django.db.models import Q

from apps.user.models import User


class ProfileFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    ordering = filters.OrderingFilter(
        fields=(
            ('email', 'email'),
            ('first_name', 'first_name'),
            ('last_name', 'last_name'),
            ('gender', 'gender'),
            ('os', 'os'),
            ('is_active', 'is_active'),
            ('is_staff', 'is_staff'),
            ('id', 'id'),
        ),
        field_labels={
            'email': 'User email',
            'first_name': 'User firstname',
            'last_name': 'User lastname',
            'gender': 'User gender',
            'os': 'User os',
            'is_active': 'User is active',
            'is_staff': 'User is staff',
            'id': 'User ID',
        }
    )

    class Meta:
        model = User
        fields = []

    def filter_search(self, queryset, name, value):
        query = Q()

        query |= Q(first_name__icontains=value)

        query |= Q(last_name__icontains=value)

        if any(char.isdigit() for char in value):
            query |= Q(phone__icontains=value)

        query |= Q(email__icontains=value)

        if value.isdigit():
            query |= Q(id=value)

        return queryset.filter(query)
