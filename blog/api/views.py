from rest_framework.views import APIView
from rest_framework.response import Response
from blog.models import Post
from blog.serializers import PostSerializer
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

class StandardPagnition(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 10
class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = StandardPagnition
    
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['title', 'excerpt', 'content', 'author']
    filterset_fields = ['category', 'author', 'tags']
    lookup_field = 'slug'