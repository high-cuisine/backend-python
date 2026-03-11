import django_filters
from django_filters import rest_framework as filters
from django.db.models import Q

from apps.common.models import Ads


class ADSFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    ordering = filters.OrderingFilter(
        fields=(
            ('title', 'title'),
            ('target_audience', 'target_audience'),
            ('id', 'id'),
        ),
        field_labels={
            'title': 'ADS title',
            'target_audience': 'ADS target_audience',
            'id': 'ADS ID',
        }
    )

    class Meta:
        model = Ads
        fields = []

    def filter_search(self, queryset, name, value):
        query = Q()

        query |= Q(title__icontains=value)

        query |= Q(description__icontains=value)

        return queryset.filter(query)