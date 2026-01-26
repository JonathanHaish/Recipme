from django.urls import path
from .views import UserProfileView, GoalListView, DietTypeListView

urlpatterns = [
    path('me', UserProfileView.as_view(), name='user-profile'),
    path('goals/', GoalListView.as_view(), name='goals-list'),
    path('diet-types/', DietTypeListView.as_view(), name='diet-types-list'),
]
