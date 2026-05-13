import logging
import time
import cv2
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def start_stream_task(self, session_id: int) -> None:
    """Запускает RTSP-поток для сессии."""
    from .models import StreamSession

    try:
        session = StreamSession.objects.select_related("camera").get(pk=session_id)
    except StreamSession.DoesNotExist:
        logger.error("StreamSession %d not found", session_id)
        return

    session.mark_running()
    cap = cv2.VideoCapture(session.camera.rtsp_url)

    if not cap.isOpened():
        session.mark_error("Не удалось открыть RTSP-поток")
        logger.error("Cannot open stream: %s", session.camera.rtsp_url)
        return

    # Сохраняем параметры потока
    fps = cap.get(cv2.CAP_PROP_FPS) or 0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    session.fps = fps
    session.resolution = f"{width}x{height}"
    session.save(update_fields=["fps", "resolution"])

    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    last_ping = time.time()
    PING_INTERVAL = 5  # секунд

    try:
        while True:
            # Проверяем не остановили ли сессию извне
            session.refresh_from_db()
            if not session.is_active:
                logger.info("Session %d stopped externally", session_id)
                break

            ret, frame = cap.read()
            if not ret or frame is None:
                session.mark_error("Потерян поток")
                break

            # Пингуем БД раз в PING_INTERVAL секунд
            if time.time() - last_ping >= PING_INTERVAL:
                session.ping()
                last_ping = time.time()

    except Exception as exc:
        logger.exception("Stream error for session %d: %s", session_id, exc)
        session.mark_error(str(exc))
    finally:
        cap.release()
        if session.status == StreamSession.Status.RUNNING:
            session.mark_stopped()


@shared_task
def stop_stream_task(session_id: int) -> None:
    """Останавливает сессию — Celery воркер сам завершит цикл."""
    from .models import StreamSession

    try:
        session = StreamSession.objects.get(pk=session_id)
        session.mark_stopped()
        logger.info("Session %d marked as stopped", session_id)
    except StreamSession.DoesNotExist:
        logger.error("StreamSession %d not found", session_id)

@shared_task(bind=True, max_retries=3)
def start_stream_task(self, session_id: int, rtsp_url: str) -> None:
    from .models import StreamSession

    try:
        session = StreamSession.objects.select_related("camera").get(pk=session_id)
    except StreamSession.DoesNotExist:
        logger.error("StreamSession %d not found", session_id)
        return

    session.mark_running()
    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        session.mark_error(f"Не удалось открыть RTSP-поток: {rtsp_url}")
        logger.error("Cannot open stream: %s", rtsp_url)
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    session.fps = fps
    session.resolution = f"{width}x{height}"
    session.save(update_fields=["fps", "resolution"])
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    last_ping = time.time()

    try:
        while True:
            session.refresh_from_db()
            if not session.is_active:
                break

            ret, frame = cap.read()
            if not ret or frame is None:
                session.mark_error("Потерян поток")
                break

            if time.time() - last_ping >= 5:
                session.ping()
                last_ping = time.time()

    except Exception as exc:
        logger.exception("Stream error for session %d: %s", session_id, exc)
        session.mark_error(str(exc))
    finally:
        cap.release()
        if session.status == StreamSession.Status.RUNNING:
            session.mark_stopped()