from django.contrib import admin
from .models import StreamSession


@admin.register(StreamSession)
class StreamSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "camera", "status", "is_active", "started_at")
    list_filter = ("status", "is_active")