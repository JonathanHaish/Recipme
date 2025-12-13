"""
URL configuration for API Management app.
"""

from django.urls import path
from api_management.views import api_data_view

app_name = 'api_management'

urlpatterns = [
    path('',api_data_view,name='api_data_view')
    
]