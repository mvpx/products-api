from django.db.models import Q
from django_filters.rest_framework import CharFilter, FilterSet

from .models import Product


class ProductFilterSet(FilterSet):
    query = CharFilter(method="filter_query")

    def filter_query(self, queryset, name, value):
        search_query = Q(
            Q(id__contains=value) | Q(name__contains=value) | Q(price__contains=value) | Q(rating__contains=value)
        )
        return queryset.filter(search_query)

    class Meta:
        model = Product
        fields = (
            "query",
            "id",
            "name",
            "price",
            "rating",
            "updated_at",
        )
