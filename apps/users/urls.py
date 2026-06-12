# apps/users/urls.py

from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    RegisterView,
    MeView,
    UsersListView,
    UserDetailView,
    ChangeUserRoleView,
    DeleteUserView,
)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", TokenObtainPairView.as_view()),
    path("refresh/", TokenRefreshView.as_view()),

    path("me/", MeView.as_view()),

    # admin only
    path("", UsersListView.as_view()),
    path("<int:pk>/", UserDetailView.as_view()),
    path("<int:pk>/role/", ChangeUserRoleView.as_view()),
    path("<int:pk>/delete/", DeleteUserView.as_view()),
]