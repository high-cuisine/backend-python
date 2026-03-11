import django_filters
from django_filters import rest_framework as filters
from django.db.models import Q

from apps.channel.models import Ticket


class TicketFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    ordering = filters.OrderingFilter(
        fields=(
            ('user_email', 'user__email'),
            ('created_at', 'created_at'),
            ('id', 'id'),
        ),
        field_labels={
            'user': 'Ticket user email',
            'created_at': 'Ticket created at',
            'id': 'Ticket ID',
        }
    )

    class Meta:
        model = Ticket
        fields = []

    def filter_search(self, queryset, name, value):
        query = Q()

        if any(char.isdigit() for char in value):
            query |= Q(user__phone__icontains=value)

        query |= Q(user__email__icontains=value)

        if value.isdigit():
            query |= Q(id=value)
            query |= Q(user_id=value)

        return queryset.filter(query)
