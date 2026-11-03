from django.core.paginator import Paginator
from .models import Post, Category
from django.shortcuts import render


def blog_list(request):

    posts = Post.objects.all().order_by("-published_date")

    category_slug = request.GET.get("category")

    if category_slug:
        posts = posts.filter(category__slug=category_slug)

    paginator = Paginator(posts, 5)

    page_number = request.GET.get("page")

    posts = paginator.get_page(page_number)

    categories = Category.objects.all()

    current_category = None

    if category_slug:
        current_category = categories.filter(slug=category_slug).first()

    return render(
        request,
        "blog/post_list.html",
        {
            "posts": posts,
            "categories": categories,
            "current_category": current_category,
        },
    )
