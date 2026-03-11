import django_filters
from django_filters import rest_framework as filters
from django.db.models import Q

from apps.user.models import Referral


class ReferralFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    ordering = filters.OrderingFilter(
        fields=(
            ('user', 'user'),
            ('code', 'code'),
            ('code_applying', 'code_applying'),
            ('id', 'id'),
        ),
        field_labels={
            'user': 'User referral',
            'code': 'Referral code',
            'code_applying': 'Referral code applying',
            'id': 'Referral code ID',
        }
    )

    class Meta:
        model = Referral
        fields = []

    def filter_search(self, queryset, name, value):
        query = Q()

        if value.isdigit():
            query |= Q(user_id=value)

        return queryset.filter(query)