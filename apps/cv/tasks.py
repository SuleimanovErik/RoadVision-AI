from celery import shared_task
from apps.images.models import RoadImage, RoadVideo
from apps.cv.services import analyze_image, analyze_video
from apps.defects.models import Defect


@shared_task
def process_image_task(image_id):
    image = RoadImage.objects.get(id=image_id)
    response = analyze_image(image.image.path)
    print("=== IMAGE CV RESULT ===", response)

    if "error" in response:
        image.delete()
        return

    # Достаём вложенный result
    result = response.get("result", response)
    detections = result.get("detections", [])

    if not detections:
        image.image.delete()
        image.delete()
        return

    for d in detections:
        Defect.objects.create(
            source_type="IMAGE",
            road_image=image,
            defect_type=d["class_name"].upper(),
            confidence=d["confidence"],
            bbox=d["bbox"],
            severity=d["severity"],
            latitude=image.latitude,
            longitude=image.longitude,
        )


@shared_task
def process_video_task(video_id):
    video = RoadVideo.objects.get(id=video_id)
    response = analyze_video(video.video.path)
    print("=== VIDEO CV RESULT ===", response)

    if "error" in response:
        print("=== ERROR, deleting video ===")
        video.delete()
        return

    # Достаём вложенный result
    result = response.get("result", response)
    frames = result.get("results", [])

    if not frames:
        print("=== NO FRAMES, deleting video ===")
        video.video.delete()
        video.delete()
        return

    total_detections = 0
    for frame_data in frames:
        timestamp = frame_data.get("timestamp")
        detections = frame_data.get("detections", [])
        for d in detections:
            Defect.objects.create(
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
            total_detections += 1

    if total_detections == 0:
        video.video.delete()
        video.delete()