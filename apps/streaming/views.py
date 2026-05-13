from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import StreamSession
from .serializers import StreamSessionSerializer
from .tasks import start_stream_task, stop_stream_task
from django.shortcuts import render
import os


def camera_view(request):
    return render(request, "camera.html", {
        "api_key": os.environ.get("INTERNAL_API_KEY", "")
    })


class StreamSessionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = StreamSession.objects.select_related("camera").order_by("-created_at")
    permission_classes = [IsAuthenticated]
    serializer_class = StreamSessionSerializer

    @action(detail=True, methods=["post"], url_path="start")
    def start(self, request, pk=None):
        session = self.get_object()
        if session.is_active:
            return Response(
                {"detail": "Сессия уже запущена."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        rtsp_url = request.data.get("rtsp_url") or session.camera.rtsp_url
        if not rtsp_url:
            return Response(
                {"detail": "Укажите rtsp_url или добавьте URL в настройках камеры."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        start_stream_task.delay(session.id, rtsp_url)
        return Response(
            {"detail": "Поток запускается.", "rtsp_url": rtsp_url},
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=["post"], url_path="stop")
    def stop(self, request, pk=None):
        session = self.get_object()
        if not session.is_active:
            return Response(
                {"detail": "Сессия не активна."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        stop_stream_task.delay(session.id)
        return Response({"detail": "Поток останавливается."}, status=status.HTTP_202_ACCEPTED)