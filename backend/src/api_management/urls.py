"""
URL configuration for API Management app.
"""

from django.urls import path
from . import views

app_name = 'api_management'

urlpatterns = [
    # Food nutrition endpoints
    path('food/<int:fdc_id>/', views.get_food_nutrition, name='get_food_nutrition'),
    
    # Custom food management
    path('custom-food/', views.save_custom_food, name='save_custom_food'),
    
    # Recipe nutrition calculation
    path('recipe/nutrition/', views.calculate_recipe_nutrition, name='calculate_recipe_nutrition'),
    
    # Health and monitoring
    path('health/', views.api_health_check, name='api_health_check'),
    
    # Documentation and examples
    path('examples/', views.api_usage_examples, name='api_usage_examples'),
]