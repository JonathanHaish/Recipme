from django.urls import path
from .views import FoodIngredientView  # וודא שהנתיב ל-views.py נכון

urlpatterns = [
    # הגדרת הנתיב ל-API. 
    # השימוש ב-.as_view() הכרחי כשמשתמשים ב-APIView של DRF
    path('api/food-lookup/', FoodIngredientView.as_view(), name='food_lookup'),
]