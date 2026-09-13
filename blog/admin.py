from django.contrib import admin
from .models import Post, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'published_date', 'author']
    search_fields = ['title', 'excerpt', 'content', 'author']
    list_filter = ['category', 'published_date']
    readonly_fields = ['published_date',]
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = [
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'author')
        }),
        ('Content', {
            'fields': ('excerpt', 'content')
        }),
        ('Publishing', {
            'fields': ('published_date',),
            'classes': ('collapse',)
        }),
    ]

    