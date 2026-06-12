# apps/images/views.py
import os

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import RoadImage, RoadVideo
from .serializers import (
    RoadImageUploadSerializer,
    RoadVideoUploadSerializer,
    RoadImageSerializer,
    RoadVideoSerializer,
)

from apps.cv.tasks import process_image_task, process_video_task


class UploadImageView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Все авторизованные пользователи

    @swagger_auto_schema(
        operation_description="Загрузка изображения дороги",
        request_body=RoadImageUploadSerializer,
        consumes=["multipart/form-data"],
        responses={
            202: openapi.Response("Image uploaded successfully"),
            400: "Bad request"
        }
    )
    def post(self, request):
        serializer = RoadImageUploadSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            image = serializer.save()

            # Отправка на обработку в CV
            process_image_task.delay(image.id)

            return Response({
                "detail": "Image uploaded",
                "id": image.id,
                "status": "pending",
            }, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UploadVideoView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Все авторизованные

    @swagger_auto_schema(
        operation_description="Загрузка видео дороги",
        request_body=RoadVideoUploadSerializer,
        consumes=["multipart/form-data"],
    )
    def post(self, request):
        serializer = RoadVideoUploadSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            video = serializer.save()
            process_video_task.delay(video.id)
            return Response({
                "detail": "Video uploaded",
                "id": video.id,
                "status": "pending",
            }, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImageHistoryView(generics.ListAPIView):
    """История загрузок изображений текущего пользователя."""
    serializer_class = RoadImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RoadImage.objects.filter(
            user=self.request.user
        ).order_by("-created_at")


class ImageDetailView(generics.RetrieveAPIView):
    """Детальная информация об изображении (только своё)."""
    serializer_class = RoadImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RoadImage.objects.filter(user=self.request.user)


class VideoHistoryView(generics.ListAPIView):
    """История загрузок видео текущего пользователя."""
    serializer_class = RoadVideoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RoadVideo.objects.filter(
            user=self.request.user
        ).order_by("-created_at")


class VideoDetailView(generics.RetrieveAPIView):
    """Детальная информация о видео (только своё)."""
    serializer_class = RoadVideoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RoadVideo.objects.filter(user=self.request.user)