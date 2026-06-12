from rest_framework import serializers
from .models import Camera


class CameraSerializer(serializers.ModelSerializer):
    """Полный сериалайзер для создания, обновления и детального просмотра камеры."""

    is_online = serializers.SerializerMethodField()
    coordinates = serializers.SerializerMethodField()
    rtsp_url = serializers.CharField(max_length=500)  # ← CharField вместо URLField

    class Meta:
        model = Camera
        fields = [
            "id",
            "name",
            "rtsp_url",
            "latitude",
            "longitude",
            "coordinates",
            "is_active",
            "is_online",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    # ------------------------------------------------------------------
    # Вычисляемые поля
    # ------------------------------------------------------------------

    def get_is_online(self, obj: Camera) -> bool:
        return obj.is_active

    def get_coordinates(self, obj: Camera) -> dict:
        return {
            "lat": float(obj.latitude),
            "lng": float(obj.longitude),
        }

    # ------------------------------------------------------------------
    # Валидация
    # ------------------------------------------------------------------

    def validate_rtsp_url(self, value: str) -> str:
        value = value.strip()
        if not value.startswith(("rtsp://", "rtsps://", "webcam://")):
            raise serializers.ValidationError(
                "URL должен начинаться с rtsp:// или rtsps://. "
                "Пример: rtsp://user:pass@192.168.1.1:554/stream"
            )
        return value

    def validate_latitude(self, value) -> float:
        if not (-90 <= float(value) <= 90):
            raise serializers.ValidationError(
                "Широта должна быть в диапазоне от -90 до 90."
            )
        return value

    def validate_longitude(self, value) -> float:
        if not (-180 <= float(value) <= 180):
            raise serializers.ValidationError(
                "Долгота должна быть в диапазоне от -180 до 180."
            )
        return value

    def validate(self, attrs: dict) -> dict:
        lat = attrs.get("latitude", getattr(self.instance, "latitude", None))
        if lat is not None and float(lat) < -60:
            raise serializers.ValidationError(
                {"latitude": "Установка камер южнее -60° не поддерживается."}
            )
        return attrs


class CameraListSerializer(serializers.ModelSerializer):
    """Лёгкий сериалайзер для списков."""

    class Meta:
        model = Camera
        fields = ["id", "name", "is_active", "latitude", "longitude"]


class CameraToggleSerializer(serializers.ModelSerializer):
    """Для эндпоинта активации/деактивации камеры."""

    class Meta:
        model = Camera
        fields = ["id", "is_active"]
        read_only_fields = ["id"]


class CameraGeoSerializer(serializers.ModelSerializer):
    """GeoJSON-совместимый сериалайзер для карты."""

    type = serializers.SerializerMethodField()
    geometry = serializers.SerializerMethodField()
    properties = serializers.SerializerMethodField()

    class Meta:
        model = Camera
        fields = ["type", "geometry", "properties"]

    def get_type(self, obj: Camera) -> str:
        return "Feature"

    def get_geometry(self, obj: Camera) -> dict:
        return {
            "type": "Point",
            "coordinates": [float(obj.longitude), float(obj.latitude)],
        }

    def get_properties(self, obj: Camera) -> dict:
        return {
            "id": obj.id,
            "name": obj.name,
            "is_active": obj.is_active,
            "rtsp_url": obj.rtsp_url,
        }