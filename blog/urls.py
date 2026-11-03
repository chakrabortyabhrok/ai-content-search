from django.urls import path, include
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.home_page, name="home"),
    path("about/", views.about_page, name="about"),
    path("blog/", views.blog_list, name="blog_list"),
    path("blog/<slug:slug>/", views.post_detail, name="post_detail"),
    path("contact/", views.contact_page, name="contact_page"),
    path("api/", include("blog.api.urls")),
]
