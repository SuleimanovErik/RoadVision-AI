# apps/defects/models.py
from django.db import models
from apps.images.models import RoadImage, RoadVideo
from apps.streaming.models import StreamSession
from apps.users.models import User
class Meta:
    unique_together = [
        # один и тот же дефект на одном кадре видео
        ["road_video", "defect_type", "timestamp_in_video", "bbox"],
        # один и тот же дефект на изображении
        ["road_image", "defect_type", "bbox"],
    ]


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
    is_rejected = models.BooleanField(default=False, verbose_name="Отклонён")
    rejected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="rejected_defects",
    )
    rejected_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.defect_type} ({self.latitude}, {self.longitude})"


class DefectCluster(models.Model):
    main_defect = models.OneToOneField(
        Defect,
        on_delete=models.CASCADE,
        related_name="cluster",
        verbose_name="Главный дефект",
    )
    cluster_key = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        verbose_name="Ключ кластера",
    )
    center_latitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        verbose_name="Широта центра",
    )
    center_longitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        verbose_name="Долгота центра",
    )
    radius_meters = models.FloatField(
        default=8.0,
        verbose_name="Радиус (м)",
    )
    defect_count = models.PositiveIntegerField(
        default=1,
        verbose_name="Количество дефектов",
    )
    max_confidence = models.FloatField(
        verbose_name="Макс. уверенность",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Кластер дефектов"
        verbose_name_plural = "Кластеры дефектов"
        indexes = [
            models.Index(fields=["center_latitude", "center_longitude"]),
            models.Index(fields=["cluster_key"]),
        ]

    def __str__(self):
        return f"Cluster {self.cluster_key} ({self.defect_count} дефектов)"