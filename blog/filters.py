import django_filters
from .models import Post

class CategoryFilterSet(django_filters.FilterSet):

    category = django_filters.CharFilter(
        field_name="category__slug", lookup_expr="icontains"
    )
    tag = django_filters.CharFilter(
        field_name="tags__slug", lookup_expr="icontains"
    )
    author = django_filters.CharFilter(
        field_name="author__name", lookup_expr="icontains"
    )

    class Meta:
        model = Post
        fields = ['category', 'tags', 'author']
