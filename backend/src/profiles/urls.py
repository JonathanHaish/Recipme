from django.urls import path
from .views import (
    UserProfileView, 
    UserProfileByUsernameView,
    GoalsListView,
    DietTypesListView
)

urlpatterns = [
    path('me', UserProfileView.as_view(), name='profile-me'),
    path('username/<str:username>', UserProfileByUsernameView.as_view(), name='profile-by-username'),
    path('goals/', GoalsListView.as_view(), name='goals-list'),
    path('diet-types/', DietTypesListView.as_view(), name='diet-types-list'),
]
