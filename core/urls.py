from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('hello/', views.hello_world, name='hello_world'),
    path('greet/<str:name>/', views.greet_user, name='greet_user'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('blog/<slug:slug>/', views.blog_post, name='blog_post'),
    path('test/', views.test_routing, name='test_routing'),

    path('about/', views.about_page, name='about_page'),
    path('contact/', views.contact_page, name='contact_page'),
    path('services/', views.services_page, name='services_page'),
    path('year/<int:year>/', views.dynamic_year, name='dynamic_year'),
    path('home/', views.home_page, name='home_page'),
]