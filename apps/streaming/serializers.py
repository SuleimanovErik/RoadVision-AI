from rest_framework import serializers
from .models import StreamSession


class StreamSessionSerializer(serializers.ModelSerializer):
    camera_name = serializers.CharField(source="camera.name", read_only=True)
    duration_seconds = serializers.FloatField(read_only=True)
    rtsp_url = serializers.CharField(
        max_length=500,
        write_only=True,
        required=False,
        allow_blank=True,
        help_text="Оставьте пустым чтобы использовать URL из настроек камеры",
    )

    class Meta:
        model = StreamSession
        fields = [
            "id",
            "camera",
            "camera_name",
            "rtsp_url",
            "status",
            "is_active",
            "fps",
            "resolution",
            "error_message",
            "started_at",
            "stopped_at",
            "last_active",
            "duration_seconds",
            "created_at",
        ]
        read_only_fields = [
            "id", "status", "is_active", "fps", "resolution",
            "error_message", "started_at", "stopped_at",
            "last_active", "created_at",
        ]

    def validate_rtsp_url(self, value: str) -> str:
        if value and not value.startswith(("rtsp://", "rtsps://")):
            raise serializers.ValidationError(
                "URL должен начинаться с rtsp:// или rtsps://"
            )
        return value

    def create(self, validated_data):
        # rtsp_url не поле модели — убираем перед созданием
        validated_data.pop("rtsp_url", None)
        return super().create(validated_data)