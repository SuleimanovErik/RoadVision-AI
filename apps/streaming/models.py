from django.db import models
from apps.cameras.models import Camera


class StreamSession(models.Model):
    STATUS_CHOICES = (
        ("idle", "Idle"),
        ("running", "Running"),
        ("error", "Error"),
    )

    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name="sessions")

    is_active = models.BooleanField(default=False)

    started_at = models.DateTimeField(null=True, blank=True)
    last_active = models.DateTimeField(null=True, blank=True)

    fps = models.FloatField(null=True, blank=True)
    resolution = models.CharField(max_length=50, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="idle")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.camera.name} ({self.status})"