import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import RoadImage, RoadVideo
from .serializers import (
    RoadImageUploadSerializer,
    RoadVideoUploadSerializer,
)

from apps.cv.tasks import process_image_task, process_video_task
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi




class UploadImageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Upload road image",
        request_body=RoadImageUploadSerializer,
        consumes=["multipart/form-data"],
        responses={
            201: openapi.Response("Image uploaded"),
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

            # 🚀 отправка в CV микросервис (асинхронно)
            process_image_task.delay(image.id)

            return Response(
                {
                    "detail": "Image uploaded",
                    "status": "processing"
                },
                status=status.HTTP_202_ACCEPTED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)













class UploadVideoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Upload road video",
        request_body=RoadVideoUploadSerializer,
        consumes=["multipart/form-data"],  # 🔥 тоже нужно
    )
    def post(self, request):
        serializer = RoadVideoUploadSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            video = serializer.save()

            process_video_task.delay(video.id)

            return Response(
                {
                    "detail": "Video uploaded",
                    "status": "processing"
                },
                status=status.HTTP_202_ACCEPTED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)