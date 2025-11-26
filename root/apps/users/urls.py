# apps/users/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UsersListCreateAPIView,
    UserDetailAPIView,
    UserMeAPIView,
    CustomTokenObtainView,
    SwitchOrgAPIView,
)

urlpatterns = [
    # Users list (GET for admins) and registration (POST public)
    path("users", UsersListCreateAPIView.as_view(), name="users-list-create"),

    # User detail (retrieve/update/patch/delete) — requires auth + AdminOrSelf
    path("users/<int:pk>", UserDetailAPIView.as_view(), name="user-detail"),

    # Current user's profile (GET / PUT / PATCH)
    path("users/me", UserMeAPIView.as_view(), name="user-me"),

    # Authentication token obtain (login)
    path("login", CustomTokenObtainView.as_view(), name="token_obtain_pair"),

    # Token refresh (SimpleJWT provided view)
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),

    # Switch organization (authenticated)
    path("switch-org", SwitchOrgAPIView.as_view(), name="auth-switch-org"),
]
