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
    search_fields = ["title", "excerpt", "content", "author", "status"]
    list_filter = ["category", "published_date", "status"]
    prepopulated_fields = {"slug": ("title",)}

    fieldsets = [
        ("Basic Information", {"fields": ("title", "slug", "category", "author")}),
        ("Content", {"fields": ("excerpt", "content")}),
        ("Publishing", {"fields": ("published_date",), "classes": ("collapse",)}),
        ("Status", {"fields": (f"{Post.status}",), "classes": ("collapse",)}),
        ("Tags", {"fields": (f"{Post.tags}")}),
    ]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = [
        "name",
    ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(post_count=Count("post"))

    @admin.display(ordering="post_count", description="Total Posts")
    def get_post_count(self, obj):
        return obj.post_count


@admin.register(Author)
class Authoradmin(admin.ModelAdmin):
    list_display = ["name", "email", "bio"]
    search_fields = ["name"]
    list_filter = ["name"]

    # readonly_fields = ["bio"]
