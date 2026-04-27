from django.contrib import admin
from .models import RoadImage, RoadVideo


@admin.register(RoadImage)
class RoadImageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'latitude',
        'longitude',
        'has_defects',
        'created_at'
    )
    list_filter = ('has_defects', 'created_at')
    search_fields = ('user__username', 'address')


@admin.register(RoadVideo)
class RoadVideoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'latitude',
        'longitude',
        'has_defects',
        'created_at'
    )
    list_filter = ('has_defects', 'created_at')
    search_fields = ('user__username', 'address')