import django_filters


class CategoryFilterSet(django_filters.FilterSet):

    category = django_filters.CharFilter(
        field_name='category__slug',lookup_expr='icontains'
    )