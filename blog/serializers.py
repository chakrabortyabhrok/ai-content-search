from .models import Post, Category, Tag, Author
from rest_framework import serializers


class PostSerializer(serializers.ModelSerializer):

    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False, allow_null=True
    )
    author = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(), required=False, allow_null=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=False
    )

    class Meta:
        model = Post
        fields = [
            "title",
            "slug",
            "excerpt",
            "content",
            "category",
            "published_date",
            "author",
            "tags",
            "status",
        ]

    def to_representation(self, instance):
        """
        READ operations (GET) return human-readable names/slugs
        instead of raw integer foreign key IDs.
        """
        rep = super().to_representation(instance)

        # Returns string name/slug for single relations, list of names for ManyToMany tags
        rep["category"] = instance.category.name if instance.category else None
        rep["author"] = instance.author.name if instance.author else None
        rep["tags"] = [tag.name for tag in instance.tags.all()]

        return rep


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name", "slug"]


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ["name", "slug"]
