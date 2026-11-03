from django.contrib import admin
from django.db.models import Count
from .models import Post, Category, Tag, Author
from rag.indexer import index_post
from rag.models import Sentence


@admin.register(Sentence)
class SentenceAdmin(admin.ModelAdmin):
    """Read-only window into the index. The single door stays shut:
    nothing here can create, edit, or delete a sentence."""

    list_display = [
        "post",
        "para_index",
        "sent_index",
        "section",
        "is_code",
        "has_embedding",
    ]
    list_filter = ["post", "is_code", "section"]
    search_fields = ["text", "section"]
    ordering = ["post__title", "para_index", "sent_index"]

    exclude = [
        "embedding"
    ]  # a 1024-float wall of numbers; the boolean below tells you what matters

    @admin.display(boolean=True, description="embedded?")
    def has_embedding(self, obj):
        return obj.embedding is not None

    # Look, don't touch — all three write paths closed.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.action(description="Reindex selected posts (RAG)")
def reindex_posts(modeladmin, request, queryset):
    posts = sentences = 0
    for post in queryset:
        sentences += index_post(post)
        posts += 1
    modeladmin.message_user(
        request, f"Reindexed {posts} posts ({sentences} sentences)."
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "published_date", "author", "status"]
    search_fields = [
        "title",
        "excerpt",
        "content",
        "status",
        "author__name",
        "category__name",
        "tags__name",
    ]
    list_filter = ["category", "published_date", "status", "author", "tags"]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)

    actions = [reindex_posts]

    fieldsets = [
        ("Basic Information", {"fields": ("title", "slug", "category", "author")}),
        ("Content", {"fields": ("excerpt", "content")}),
        ("Publishing", {"fields": ("published_date",), "classes": ("collapse",)}),
        ("Status", {"fields": ("status",), "classes": ("collapse",)}),
        ("Tags", {"fields": ("tags",)}),
    ]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = [
        "name",
    ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(post_count=Count("posts"))

    @admin.display(ordering="post_count", description="Total Posts")
    def get_post_count(self, obj):
        return obj.post_count

    list_display = ["name", "slug", "get_post_count"]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "bio"]
    search_fields = ["name"]
