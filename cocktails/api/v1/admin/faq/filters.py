import django_filters
from django_filters import rest_framework as filters
from django.db.models import Q

from apps.common.models import Ads, FAQ


class FAQFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    ordering = filters.OrderingFilter(
        fields=(
            ('question', 'question'),
            ('answer', 'answer'),
            ('id', 'id'),
        ),
        field_labels={
            'question': 'FAQ question',
            'answer': 'FAQ answer',
            'id': 'FAQ ID',
        }
    )

    class Meta:
        model = FAQ
        fields = []

    def filter_search(self, queryset, name, value):
        query = Q()

        query |= Q(question__icontains=value)

        query |= Q(answer__icontains=value)

        return queryset.filter(query)