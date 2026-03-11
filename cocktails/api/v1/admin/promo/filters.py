import django_filters
from django_filters import rest_framework as filters
from django.db.models import Q

from apps.goods.models import Promo, PurchasedPromo


class PromoFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    ordering = filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('price', 'price'),
            ('id', 'id'),
        ),
        field_labels={
            'name': 'Promo name',
            'price': 'Promo price',
            'id': 'Promo ID',
        }
    )

    class Meta:
        model = Promo
        fields = []

    def filter_search(self, queryset, name, value):
        query = Q()

        query |= Q(name__icontains=value)

        query |= Q(description__icontains=value)

        return queryset.filter(query)


class PurchasedPromoFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    ordering = filters.OrderingFilter(
        fields=(
            ('user', 'user'),
            ('purchased_at', 'purchased_at'),
            ('id', 'id'),
        ),
        field_labels={
            'user': 'User purchased promo',
            'purchased_at': 'Promo purchased at',
            'id': 'Purchased promo ID',
        }
    )

    class Meta:
        model = PurchasedPromo
        fields = []

    def filter_search(self, queryset, name, value):
        query = Q()

        if value.isdigit():
            query |= Q(user_id=value)

        query |= Q(purchased_at__icontains=value)

        return queryset.filter(query)