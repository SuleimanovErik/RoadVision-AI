import os
import base64
import logging
import requests
from celery import shared_task

logger = logging.getLogger(__name__)

CV_SERVICE_URL = os.environ.get('CV_SERVICE_URL', 'http://92.38.35.9:8080')
CV_API_KEY = os.environ.get('INTERNAL_API_KEY', '')


def get_headers():
    return {"X-API-Key": CV_API_KEY} if CV_API_KEY else {}


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def start_stream_task(self, session_id: int, rtsp_url: str) -> None:
    from .models import StreamSession

    try:
        session = StreamSession.objects.select_related("camera").get(pk=session_id)
    except StreamSession.DoesNotExist:
        logger.error("StreamSession %d not found", session_id)
        return

    if rtsp_url == 'webcam://local':
        session.mark_running()
        logger.info("Session %d started as webcam (frontend)", session_id)
        return

    session.mark_running()

    try:
        r = requests.post(
            f"{CV_SERVICE_URL}/rtsp/start",
            json={"url": rtsp_url},
            headers=get_headers(),
            timeout=10,
        )
        if r.status_code != 200:
            session.mark_error(f"CV error {r.status_code}: {r.text}")
            logger.error("CV start failed session=%s status=%s body=%s",
                         session_id, r.status_code, r.text)
            return
        logger.info("Session %d RTSP started via CV", session_id)

    except requests.exceptions.RequestException as exc:
        session.mark_error(str(exc))
        logger.exception("CV service unreachable: %s", exc)
        raise self.retry(exc=exc)


@shared_task(bind=True)
def stop_stream_task(self, session_id: int) -> None:
    from .models import StreamSession

    try:
        session = StreamSession.objects.get(pk=session_id)
    except StreamSession.DoesNotExist:
        logger.error("StreamSession %d not found", session_id)
        return

    try:
        requests.post(f"{CV_SERVICE_URL}/rtsp/stop",
                      headers=get_headers(), timeout=5)
    except requests.exceptions.RequestException as e:
        logger.warning("CV stop failed: %s", e)

    session.mark_stopped()
    logger.info("Session %d stopped", session_id)


@shared_task
def process_webcam_frame(frame_b64: str, latitude: float,
                          longitude: float, session_id: int) -> None:
    """Принимает кадр от фронта, отправляет в CV, сохраняет дефекты, пушит в WS."""
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
    from apps.defects.services import DefectService
    from .models import StreamSession

    try:
        session = StreamSession.objects.get(pk=session_id)
    except StreamSession.DoesNotExist:
        logger.error("StreamSession %d not found", session_id)
        return

    frame_bytes = base64.b64decode(frame_b64)

    try:
        resp = requests.post(
            f"{CV_SERVICE_URL}/detect/image",
            headers=get_headers(),
            files={"file": ("frame.jpg", frame_bytes, "image/jpeg")},
            timeout=15,
        )
        if resp.status_code != 200:
            logger.error("CV detect failed: %s %s", resp.status_code, resp.text)
            return
        data = resp.json()
    except requests.exceptions.RequestException as e:
        logger.error("CV service error: %s", e)
        return

    detections = data.get("result", {}).get("detections", [])
    if not detections:
        return

    channel_layer = get_channel_layer()
    group_name = f"stream_{session_id}"

    for d in detections:
        defect = DefectService.create_defect(
            source_type="STREAM",
            defect_type=d["class_name"].upper(),
            confidence=d["confidence"],
            bbox=d["bbox"],
            severity=d["severity"],
            latitude=latitude,
            longitude=longitude,
            stream_session=session,
        )
        if defect:
            # пушим детекцию в WebSocket
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "stream.detection",
                    "data": {
                        "defect_type": defect.defect_type,
                        "confidence": defect.confidence,
                        "bbox": defect.bbox,
                        "severity": defect.severity,
                        "latitude": float(defect.latitude),
                        "longitude": float(defect.longitude),
                    }
                }
            )
            logger.info("Defect saved and pushed: %s session=%d",
                        defect.defect_type, session_id)