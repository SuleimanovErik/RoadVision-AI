from celery import shared_task
from apps.defects.models import Defect
from apps.images.models import RoadImage, RoadVideo
from apps.cv.services import analyze_image, analyze_video


@shared_task
def process_video_task(video_id):
    video = RoadVideo.objects.get(id=video_id)

    if Defect.objects.filter(road_video=video).exists():
        return

    response = analyze_video(video.video.path)
    if "error" in response:
        video.delete()
        return

    result = response.get("result", response)
    frames = result.get("results", [])
    if not frames:
        video.video.delete()
        video.delete()
        return

    # Дедупликация: одна яма не может появиться снова раньше чем через 3 секунды
    DEDUP_WINDOW = 3.0  # секунд
    seen = {}  # {defect_type: last_timestamp}

    total = 0
    for frame_data in frames:
        timestamp = frame_data.get("timestamp") or 0
        for d in frame_data.get("detections", []):
            defect_type = d["class_name"].upper()
            last_seen = seen.get(defect_type)

            # Пропускаем если видели этот тип дефекта недавно
            if last_seen is not None and (timestamp - last_seen) < DEDUP_WINDOW:
                continue

            seen[defect_type] = timestamp

            Defect.objects.create(
                source_type="VIDEO",
                road_video=video,
                defect_type=defect_type,
                confidence=d["confidence"],
                bbox=d["bbox"],
                severity=d["severity"],
                latitude=video.latitude,
                longitude=video.longitude,
                timestamp_in_video=timestamp,
            )
            total += 1

    if total == 0:
        video.video.delete()
        video.delete()