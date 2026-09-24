from .views import PostViewSet, CategoryViewSet, TagViewSet, AuthorViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'authors', AuthorViewSet, basename='author')

urlpatterns = router.urls
