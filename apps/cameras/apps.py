from django.apps import AppConfig


class CamerasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.cameras"  # ← полный путь, не просто "cameras"
    verbose_name = "Камеры"
