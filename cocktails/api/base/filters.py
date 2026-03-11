from django_filters import rest_framework as filters


class QuestItemFilterSet(filters.FilterSet):
    quest = filters.NumberFilter(field_name='recipe')
