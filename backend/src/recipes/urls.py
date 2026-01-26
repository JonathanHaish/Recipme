from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, TagViewSet

# Create a router that automatically generates all URLs for us
router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'tags', TagViewSet, basename='tag')

urlpatterns = [
    # Connect all router URLs (GET, POST, PUT, DELETE)
    path('', include(router.urls)),
]
