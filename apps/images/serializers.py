from rest_framework import serializers
from .models import RoadImage, RoadVideo


class RoadImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoadImage
        fields = [
            'id',
            'image',
            'latitude',
            'longitude',
            'address',
            'timestamp',
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        return RoadImage.objects.create(
            user=request.user,
            file_size=validated_data['image'].size,
            **validated_data
        )


class RoadImageSerializer(serializers.ModelSerializer):
    """Для просмотра истории и статуса."""
    class Meta:
        model = RoadImage
        fields = [
            'id',
            'image',
            'thumbnail',
            'latitude',
            'longitude',
            'address',
            'timestamp',
            'status',
            'has_defects',
            'file_size',
            'processing_time',
            'created_at',
        ]
        read_only_fields = fields


class RoadVideoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoadVideo
        fields = [
            'id',
            'video',
            'latitude',
            'longitude',
            'address',
            'timestamp',
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        return RoadVideo.objects.create(
            user=request.user,
            file_size=validated_data['video'].size,
            **validated_data
        )


class RoadVideoSerializer(serializers.ModelSerializer):
    """Для просмотра истории и статуса."""
    class Meta:
        model = RoadVideo
        fields = [
            'id',
            'video',
            'thumbnail',
            'latitude',
            'longitude',
            'address',
            'timestamp',
            'status',
            'has_defects',
            'duration',
            'file_size',
            'created_at',
        ]
        read_only_fields = fields