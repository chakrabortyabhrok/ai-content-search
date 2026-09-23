import django_filters
from blog.models import Post, Category, Tag, Author
from blog.serializers import PostSerializer, CategorySerializer, TagSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

class StandardPagnition(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["name"]
    lookup_field = "slug"

class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["name"]
    lookup_field = "slug"


class CategoryFilterSet(django_filters.FilterSet):

    category = django_filters.CharFilter(
        field_name='category__slug',lookup_expr='icontains'
    )

class PostViewSet(ModelViewSet):

    serializer_class = PostSerializer
    pagination_class = StandardPagnition

    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["title", "excerpt", "content", "author__name"]
    filterset_class = CategoryFilterSet

    filterset_fields = ["category__slug", "author__name", "tags__slug"]
    lookup_field = "slug"

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return Post.objects.all()

        return Post.objects.filter(status="published")