from django.contrib import admin
from .models import StreamSession


@admin.register(StreamSession)
class StreamSessionAdmin(admin.ModelAdmin):
    list_display = ["id", "camera", "status", "is_active", "fps", "resolution", "started_at", "stopped_at"]
    list_filter = ["status", "is_active"]
    search_fields = ["camera__name"]
    readonly_fields = ["created_at", "started_at", "stopped_at", "last_active", "get_duration"]
    ordering = ["-created_at"]

    fieldsets = (
        ("Основное", {"fields": ("camera", "status", "is_active")}),
        ("Параметры потока", {"fields": ("fps", "resolution")}),
        ("Время", {"fields": ("started_at", "stopped_at", "last_active", "get_duration", "created_at")}),
        ("Ошибка", {"fields": ("error_message",), "classes": ("collapse",)}),
    )

    @admin.display(description="Длительность (сек)")
    def get_duration(self, obj):
        d = obj.duration_seconds
        return f"{d:.1f} сек" if d is not None else "—"