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
            'timestamp'
        ]

    def create(self, validated_data):
        request = self.context.get('request')

        return RoadImage.objects.create(
            user=request.user,
            file_size=validated_data['image'].size,
            **validated_data
        )


class RoadVideoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoadVideo
        fields = [
            'id',
            'video',
            'latitude',
            'longitude',
            'address',
            'timestamp'
        ]

    def create(self, validated_data):
        request = self.context.get('request')

        return RoadVideo.objects.create(
            user=request.user,
            file_size=validated_data['video'].size,
            **validated_data
        )