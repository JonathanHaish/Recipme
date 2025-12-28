from django.urls import path
from .views import (
    RegisterView, 
    LoginView, 
    LogoutView, 
    RefreshView, 
    UserView,
    ForgotPasswordView,
    ResetPasswordView
)

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('refresh', RefreshView.as_view(), name='token_refresh'),
    path('me', UserView.as_view(), name='user'),
    path('forgot-password', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password', ResetPasswordView.as_view(), name='reset_password'),
]

