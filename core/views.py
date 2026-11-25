from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .forms import ContactForm

User = get_user_model()

def home_page(request):
    return render(request, 'core/home.html')

def about_page(request):
    return render(request, 'core/about.html')

def hello_world(request):
    return HttpResponse("<h1>Hello World from Django!</h1>")

def greet_user(request, name):
    return HttpResponse(f"<h1>Hello, {name.capitalize()}!<h1>")

def post_detail(request, post_id):
    return HttpResponse(f"<h1>Post Detail - ID: {post_id}<h1>")

def blog_post(request, slug):
    return HttpResponse(f"<h1>Blog Post - Slug: {slug}<h1>")

def test_routing(request):
    return HttpResponse(f"<h1>URL Routing is working perfectly!<h1>")

def services_page(request):
    return HttpResponse("<h1>Our Services</h1><ul><li>Web Development</li><li>AI Integration</li></ul>")

def dynamic_year(request, year):
    return HttpResponse(f"<h1>Year: {year}</h1><p>This is a dynamic page for {year}</p>")

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get("username", "").strip()
    email = request.data.get("email", "").strip()
    password = request.data.get("password", "")

    if not username or not password:
        return Response({"error": "username and password required"}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "username taken"}, status=400)

    try:
        validate_password(password)
    except ValidationError as e:
        return Response({"error": e.messages}, status=400)

    user = User.objects.create_user(username=username, email=email, password=password)
    return Response({"id": user.id, "username": user.username}, status=201)


def contact_page(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        
        if form.is_valid():
            print("✅ Form submitted successfully!")
            print(form.cleaned_data)
            return render(request, 'core/contact_success.html', {'form' : form})
        
    else:
        form = ContactForm()
    return render(request, 'core/contact.html', {'form' : form})
