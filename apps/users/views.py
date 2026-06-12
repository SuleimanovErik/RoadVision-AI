# apps/users/views.py

from django.contrib.auth import get_user_model

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics, permissions, status


from .serializers import (
    RegisterSerializer,
    UserSerializer,
    UpdateProfileSerializer,
    ChangeRoleSerializer,
)

from .permissions import IsAdmin


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]



class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UpdateProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user

class UsersListView(generics.ListAPIView):
    queryset = User.objects.all().order_by("-id")
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


class ChangeUserRoleView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ChangeRoleSerializer
    permission_classes = [IsAdmin]


class DeleteUserView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAdmin]