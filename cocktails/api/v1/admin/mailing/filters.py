import django_filters
from django_filters import rest_framework as filters
from django.db.models import Q

from apps.common.models import Ads, Mailing


class MailingFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    ordering = filters.OrderingFilter(
        fields=(
            ('title', 'title'),
            ('title_eng', 'title_eng'),
            ('id', 'id'),
        ),
        field_labels={
            'title': 'Mailing title',
            'title_eng': 'Mailing english title',
            'id': 'Mailing ID',
        }
    )

    class Meta:
        model = Mailing
        fields = []

    def filter_search(self, queryset, name, value):
        query = Q()

        query |= Q(title__icontains=value)

        query |= Q(description__icontains=value)

        query |= Q(title_eng__icontains=value)

        query |= Q(description_eng__icontains=value)

        return queryset.filter(query)
