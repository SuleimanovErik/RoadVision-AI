from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {
            "fields": ("role", "phone")
        }),
    )

    list_display = (
        "id",
        "username",
        "email",
        "role",
        "is_active",
        "is_staff",
    )