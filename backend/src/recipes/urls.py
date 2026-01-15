from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet

# יצירת ראוטר שיוצר עבורנו את כל הכתובות באופן אוטומטי
router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    # מחבר את כל הכתובות של הראוטר (GET, POST, PUT, DELETE)
    path('', include(router.urls)),
]
