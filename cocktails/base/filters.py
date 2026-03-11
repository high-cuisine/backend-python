from django_admin_listfilter_dropdown.filters import RelatedOnlyDropdownFilter as BaseRelatedOnlyDropdownFilter
from django_filters import rest_framework as filters


class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class ChoiceInFilter(filters.BaseInFilter, filters.ChoiceFilter):
    pass


class DashSeparatedListFilter(filters.BaseCSVFilter, filters.NumberFilter):
    def filter(self, qs, value):
        if value:
            if isinstance(value, str):
                value = value.replace('-', ',').split(',')
            elif isinstance(value, list):
                value = ','.join(str(v) for v in value).replace('-', ',').split(',')
            try:
                value = [int(v) for v in value]
            except ValueError:
                return qs.none()
        return super().filter(qs, value if value else [])


class RelatedOnlyDropdownFilter(BaseRelatedOnlyDropdownFilter):
    def field_choices(self, field, request, model_admin):
        field_choices = super().field_choices(field, request, model_admin)
        return sorted(field_choices, key=lambda i: i[1])
