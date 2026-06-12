# apps/users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Roles(models.TextChoices):
        USER = "user", "User"
        OPERATOR = "operator", "Operator"
        ADMIN = "admin", "Admin"

    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.USER
    )

    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    # ==================== PROPERTIES ====================
    @property
    def is_admin(self):
        return self.role == self.Roles.ADMIN

    @property
    def is_operator(self):
        return self.role in (self.Roles.OPERATOR, self.Roles.ADMIN)  # ← ИСПРАВИЛ

    @property
    def is_user(self):
        return self.role == self.Roles.USER