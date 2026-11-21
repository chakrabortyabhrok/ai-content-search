import django_filters
from blog.models import Post, Category, Tag, Author
from blog.serializers import PostSerializer, CategorySerializer, TagSerializer, AuthorSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from ..filters import CategoryFilterSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rag.answer import AskError, ask

MAX_QUESTION_LENGTH = 500

class StandardPagnition(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10
class PostViewSet(ModelViewSet):

    serializer_class = PostSerializer
    pagination_class = StandardPagnition

    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["title", "excerpt", "content", "author__name"]
    filterset_class = CategoryFilterSet
    lookup_field = "slug"

    def get_queryset(self):
        # user = self.request.user
        # if user.is_authenticated and user.is_staff:
        #     return Post.objects.all().select_related('category', 'author').prefetch_related('tags')

        return (
            Post.objects.filter(status="published")
            .select_related('category', 'author')
            .prefetch_related('tags')
        )

    # POST /api/posts/ask_ai/  {"question": "..."} -> {"answer": ..., "sources": [...]}
    # Open to anyone: no REST_FRAMEWORK block in settings, so DRF defaults to AllowAny.
    # Thin on purpose: validate -> ask() -> Response. All RAG logic lives in rag/answer.py.
    @action(detail=False, methods=["post"], url_path="ask_ai")
    def ask_ai(self, request):
        question = request.data.get("question")

        # isinstance first: {"question": 123} would crash on .strip() -> 500
        if not isinstance(question, str) or not question.strip():
            return Response(
                {"error": "Field 'question' is required and must be non-empty text."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        question = question.strip()
        if len(question) > MAX_QUESTION_LENGTH:
            return Response(
                {"error": f"Question too long (max {MAX_QUESTION_LENGTH} characters)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = ask(question)
        except AskError as exc:
            # 502 Bad Gateway: OUR server is fine, a service we depend on failed.
            return Response({"error": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        return Response(result)


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

class AuthorViewSet(ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [DjangoFilterBackend]
    search_fields = ["name"]
    filterset_fields = ["name"]
    lookup_field = "name"