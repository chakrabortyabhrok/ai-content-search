import random
from django.utils import timezone
from blog.models import Category, Tag, Author, Post

# 1. Data Definitions
POSTS_DATA = [
    {
        "title": "Getting Started with Python and Django",
        "slug": "getting-started-python-django",
        "excerpt": "A comprehensive beginner's guide...",
        "content": "Django is a high-level Python web framework...",
        "status": "published",
        "category_slug": "digital-computing",
        "tag_slugs": ["software-development", "technology"],
        "author_name": "Rohan Verma",
    },
    # Add all your remaining posts here...
]

# 2. Execution Logic
created_count = 0
updated_count = 0

for data in POSTS_DATA:
    category = Category.objects.filter(slug=data["category_slug"]).first()
    author = Author.objects.filter(name=data["author_name"]).first()

    post, created = Post.objects.update_or_create(
        slug=data["slug"],
        defaults={
            "title": data["title"],
            "excerpt": data["excerpt"],
            "content": data["content"],
            "status": data["status"],
            "category": category,
            "author": author,
            "published_date": timezone.now() if data["status"] == "published" else None,
        },
    )

    if "tag_slugs" in data:
        matched_tags = Tag.objects.filter(slug__in=data["tag_slugs"])
        post.tags.set(matched_tags)

    if created:
        created_count += 1
    else:
        updated_count += 1

print(f"Done! Created: {created_count}, Updated: {updated_count}")
print(f"Total Posts in DB: {Post.objects.count()}")