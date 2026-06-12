from celery import shared_task
from apps.images.models import RoadImage, RoadVideo
from apps.cv.services import analyze_image, analyze_video
from apps.defects.services import DefectService


@shared_task
def process_image_task(image_id):
    try:
        image = RoadImage.objects.get(id=image_id)
    except RoadImage.DoesNotExist:
        return

    image.status = RoadImage.Status.PROCESSING
    image.save(update_fields=["status"])

    response = analyze_image(image.image.path)

    if "error" in response:
        image.status = RoadImage.Status.FAILED
        image.save(update_fields=["status"])
        image.delete()
        return

    result = response.get("result", response)
    detections = result.get("detections", [])

    if not detections:
        image.delete()
        return

    for d in detections:
        DefectService.create_defect(
            source_type="IMAGE",
            road_image=image,
            defect_type=d["class_name"].upper(),
            confidence=d["confidence"],
            bbox=d["bbox"],
            severity=d["severity"],
            latitude=image.latitude,
            longitude=image.longitude,
        )

    image.status = RoadImage.Status.COMPLETED
    image.has_defects = True
    image.save(update_fields=["status", "has_defects"])


@shared_task
def process_video_task(video_id):
    try:
        video = RoadVideo.objects.get(id=video_id)
    except RoadVideo.DoesNotExist:
        return

    video.status = RoadVideo.Status.PROCESSING
    video.save(update_fields=["status"])

    response = analyze_video(video.video.path)

    if "error" in response:
        video.status = RoadVideo.Status.FAILED
        video.save(update_fields=["status"])
        video.delete()
        return

    result = response.get("result", response)
    frames = result.get("results", [])

    if not frames:
        video.video.delete()
        video.delete()
        return

    total_detections = 0
    for frame_data in frames:
        timestamp = frame_data.get("timestamp")
        detections = frame_data.get("detections", [])
        for d in detections:
            defect = DefectService.create_defect(
                source_type="VIDEO",
                road_video=video,
                defect_type=d["class_name"].upper(),
                confidence=d["confidence"],
                bbox=d["bbox"],
                severity=d["severity"],
                latitude=video.latitude,
                longitude=video.longitude,
                timestamp_in_video=timestamp,
            )
            if defect:
                total_detections += 1

    if total_detections == 0:
        video.video.delete()
        video.delete()
        return

    video.status = RoadVideo.Status.COMPLETED
    video.has_defects = True
    video.save(update_fields=["status", "has_defects"])