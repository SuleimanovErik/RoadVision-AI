from django.db import models
from django.conf import settings

# Create your models here.

class RoadImage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(upload_to='road_images/')
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.CharField(max_length=255, null=True, blank=True)

    timestamp = models.DateTimeField()

    file_size = models.IntegerField(null=True, blank=True)
    processing_time = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    has_defects = models.BooleanField(default=False)

    def __str__(self):
        return f"Image {self.id} by {self.user}"

class RoadVideo(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='videos'
    )

    video = models.FileField(upload_to='road_videos/')
    thumbnail = models.ImageField(upload_to='video_thumbnails/', null=True, blank=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.CharField(max_length=255, null=True, blank=True)

    timestamp = models.DateTimeField()

    duration = models.FloatField(null=True, blank=True)
    file_size = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    has_defects = models.BooleanField(default=False)

    def __str__(self):
        return f"Video {self.id} by {self.user}"