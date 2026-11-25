# from django.contrib import admin
# from django.urls import path, include

# from core.urls import auth_urlpatterns

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     *auth_urlpatterns,
#     path('', include('blog.urls')),
#     path('', include('core.urls')),
# ]

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import register

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', register, name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include('blog.urls')),
    path('', include('core.urls')),
]