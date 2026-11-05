from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterAPIView.as_view(), name="register"),
    path("login/", views.LoginAPIView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
