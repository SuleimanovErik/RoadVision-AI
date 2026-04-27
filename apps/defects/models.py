from django.db import models
from apps.images.models import RoadImage, RoadVideo
from apps.streaming.models import StreamSession
from apps.users.models import User


class Defect(models.Model):

    SOURCE_TYPES = [
        ("IMAGE", "Image"),
        ("VIDEO", "Video"),
        ("STREAM", "Stream"),
    ]

    DEFECT_TYPES = [
        ("POTHOLE", "Pothole"),
        ("CRACK", "Crack"),
        ("ALLIGATOR_CRACK", "Alligator Crack"),
        ("ROAD_MARKING", "Road Marking"),
        ("OTHER", "Other"),
    ]

    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    source_type = models.CharField(max_length=10, choices=SOURCE_TYPES)

    # источники
    road_image = models.ForeignKey(
        RoadImage, on_delete=models.CASCADE, null=True, blank=True
    )
    road_video = models.ForeignKey(
        RoadVideo, on_delete=models.CASCADE, null=True, blank=True
    )
    stream_session = models.ForeignKey(
        StreamSession, on_delete=models.CASCADE, null=True, blank=True
    )

    defect_type = models.CharField(max_length=30, choices=DEFECT_TYPES)

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    confidence = models.FloatField()
    bbox = models.JSONField()

    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)

    timestamp_in_video = models.FloatField(null=True, blank=True)

    is_confirmed = models.BooleanField(default=False)
    confirmed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    confirmed_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.defect_type} ({self.latitude}, {self.longitude})"