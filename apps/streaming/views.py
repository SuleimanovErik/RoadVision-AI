# apps/streaming/views.py
import os

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import render

from apps.users.permissions import IsOperator

from .models import StreamSession
from .serializers import StreamSessionSerializer
from .tasks import start_stream_task, stop_stream_task, process_webcam_frame


def camera_view(request):
    """Отображение страницы с веб-камерой / стримингом"""
    from rest_framework_simplejwt.tokens import AccessToken
    token = str(AccessToken.for_user(request.user)) if request.user.is_authenticated else ""
    return render(request, "camera.html", {
        "api_key": os.environ.get("INTERNAL_API_KEY", ""),
        "token": token,
    })


class StreamSessionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Управление сессиями стриминга (только Operator + Admin)
    """
    queryset = StreamSession.objects.select_related("camera").order_by("-created_at")
    permission_classes = [IsAuthenticated, IsOperator]   # ← Только Оператор и Админ
    serializer_class = StreamSessionSerializer

    @action(detail=True, methods=["post"], url_path="start")
    def start(self, request, pk=None):
        session = self.get_object()
        if session.is_active:
            return Response({"detail": "Сессия уже запущена."}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({"detail": "Сессия не активна."}, status=status.HTTP_400_BAD_REQUEST)

        stop_stream_task.delay(session.id)
        return Response({"detail": "Поток останавливается."}, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=["post"], url_path="frame")
    def frame(self, request, pk=None):
        """Фронт шлёт сюда кадры с веб-камеры"""
        session = self.get_object()
        if not session.is_active:
            return Response({"detail": "Сессия не активна."}, status=status.HTTP_400_BAD_REQUEST)

        frame_b64 = request.data.get("frame")
        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")

        if not frame_b64 or latitude is None or longitude is None:
            return Response(
                {"detail": "frame, latitude, longitude обязательны."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        process_webcam_frame.delay(
            frame_b64, float(latitude), float(longitude), session.id
        )
        return Response({"detail": "ok"}, status=status.HTTP_202_ACCEPTED)