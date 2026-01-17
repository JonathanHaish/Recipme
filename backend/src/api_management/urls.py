from django.urls import path
from .views import FoodIngredientView

urlpatterns = [
    # הגדרת הנתיב ל-API. 
    # השימוש ב-.as_view() הכרחי כשמשתמשים ב-APIView של DRF
    path('api/food-lookup/', FoodIngredientView.as_view(), name='food_lookup'),
    # Frontend endpoints - empty path for /api/ingredients/ and /api/ingredients/nutritions/
    path('', FoodIngredientView.as_view(), name='ingredients_search'),
    path('nutritions/', FoodIngredientView.as_view(), name='ingredients_nutritions'),
]