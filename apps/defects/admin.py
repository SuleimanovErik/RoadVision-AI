from django.contrib import admin
from .models import Defect

@admin.register(Defect)
class DefectAdmin(admin.ModelAdmin):
    list_display = ("id", "defect_type", "source_type", "severity", "created_at")
    list_filter = ("defect_type", "severity", "source_type")
    search_fields = ("defect_type",)