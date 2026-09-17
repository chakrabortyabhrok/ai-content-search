from django.http import HttpResponse
from django.shortcuts import render
from core.forms import ContactForm
from .models import Post, Category


def home_page(request):
    return render(request, "blog/home.html")


def about_page(request):
    return render(request, "blog/about.html")


def blog_list(request):
    category_slug = request.GET.get("category")

    categories = Category.objects.all()

    if category_slug:
        current_category = Category.objects.get(slug=category_slug)
        posts = Post.objects.filter(category=current_category).order_by(
            "-published_date"
        )
    else:
        current_category = None
        posts = Post.objects.all().order_by("-published_date")

    return render(
        request,
        "blog/post_list.html",
        {
            "posts": posts,
            "categories": categories,
            "current_category": current_category,
        },
    )


def post_detail(request, slug):
    try:
        post = Post.objects.get(slug=slug)
        return render(request, "blog/post_detail.html", {"post": post})
    except Post.DoesNotExist:
        return HttpResponse("404 - Post not found", status=404)


def contact_page(request):
    if request.method == "POST":
        form = ContactForm(request.POST)

        if form.is_valid():
            print("✅ Form submitted successfully!")
            print(form.cleaned_data)
            return render(request, "blog/contact_success.html", {"form": form})

    else:
        form = ContactForm()
    return render(request, "blog/contact.html", {"form": form})
