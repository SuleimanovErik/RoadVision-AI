from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Camera


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "is_active", "latitude", "longitude", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "rtsp_url"]
    readonly_fields = ["created_at"]
    list_editable = ["is_active"]
    ordering = ["name"]

    fieldsets = (
        (_("Основное"), {
            "fields": ("name", "rtsp_url", "is_active")
        }),
        (_("Геолокация"), {
            "fields": ("latitude", "longitude")
        }),
        (_("Метаданные"), {
            "fields": ("created_at",),
            "classes": ("collapse",),
        }),
    )