from django.urls import path
from .views import FoodIngredientView

urlpatterns = [
    # API path configuration
    # Using .as_view() is required when using DRF's APIView
    path('api/food-lookup/', FoodIngredientView.as_view(), name='food_lookup'),
    # Frontend endpoints - empty path for /api/ingredients/ and /api/ingredients/nutritions/
    path('', FoodIngredientView.as_view(), name='ingredients_search'),
    path('nutritions/', FoodIngredientView.as_view(), name='ingredients_nutritions'),
]