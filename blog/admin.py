from django.contrib import admin
from django.db.models import Count
from .models import Post, Category, Tag, Author


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "published_date", "author", "status"]
    search_fields = ["title", "excerpt", "content", "status", "author__name", "category__name", "tags__name"]
    list_filter = ["category", "published_date", "status", "author", "tags"]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)

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
class Authoradmin(admin.ModelAdmin):
    list_display = ["name", "email", "bio"]
    search_fields = ["name"]

    # readonly_fields = ["bio"]
