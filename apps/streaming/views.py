import os

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import render

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
    Управление сессиями стриминга (Временно открыто для локальной отладки веб-камеры)
    """
    queryset = StreamSession.objects.select_related("camera").order_by("-created_at")

    # ЧИСТОЕ РЕШЕНИЕ: Отключаем проверку JWT-токенов на уровне этого ViewSet
    authentication_classes = ()
    permission_classes = [AllowAny]

    serializer_class = StreamSessionSerializer

    @action(detail=True, methods=["post"], url_path="start")
    def start(self, request, pk=None):
        # Достаем сессию напрямую по pk, чтобы DRF не выкидывал HTML-404
        try:
            session = StreamSession.objects.get(pk=pk)
        except StreamSession.DoesNotExist:
            return Response({"detail": f"Сессия с ID {pk} не найдена в БД."}, status=status.HTTP_404_NOT_FOUND)

        # Берём URL или используем дефолтную заглушку, которую мы создали сигналом
        rtsp_url = request.data.get("rtsp_url") or (session.camera.rtsp_url if session.camera else None)
        if not rtsp_url:
            rtsp_url = "rtsp://127.0.0.1:554/webcam"

        start_stream_task.delay(session.id, rtsp_url)
        return Response(
            {"detail": "Поток запускается.", "rtsp_url": rtsp_url},
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=["post"], url_path="frame")
    def frame(self, request, pk=None):
        """Фронт шлёт сюда кадры с веб-камеры"""
        try:
            session = StreamSession.objects.get(pk=pk)
        except StreamSession.DoesNotExist:
            return Response({"detail": f"Сессия с ID {pk} не найдена в БД."}, status=status.HTTP_404_NOT_FOUND)

        frame_b64 = request.data.get("frame")
        latitude = request.data.get("latitude") or 42.8746  # Подстраховка геолокации
        longitude = request.data.get("longitude") or 74.5698

        if not frame_b64:
            return Response(
                {"detail": "Поле frame обязательно."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        process_webcam_frame.delay(
            frame_b64, float(latitude), float(longitude), session.id
        )
        return Response({"detail": "ok"}, status=status.HTTP_202_ACCEPTED)