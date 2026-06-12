import hashlib
from decimal import Decimal
from django.utils import timezone
from django.db import transaction, IntegrityError
from datetime import timedelta
from .models import Defect


class DefectService:

    GEO_THRESHOLD = Decimal("0.00005")
    DEDUP_WINDOW_MINUTES = 60
    CLUSTER_PRECISION = Decimal("0.0001")  # ~11м сетка

    @classmethod
    def _cluster_key(cls, defect_type: str, lat: Decimal, lng: Decimal) -> str:
        rounded_lat = (lat / cls.CLUSTER_PRECISION).quantize(Decimal("1")) * cls.CLUSTER_PRECISION
        rounded_lng = (lng / cls.CLUSTER_PRECISION).quantize(Decimal("1")) * cls.CLUSTER_PRECISION
        raw = f"{defect_type}:{rounded_lat}:{rounded_lng}"
        return hashlib.md5(raw.encode()).hexdigest()[:16]

    @classmethod
    def create_defect(
        cls,
        *,
        source_type,
        defect_type,
        confidence,
        bbox,
        severity,
        latitude,
        longitude,
        road_image=None,
        road_video=None,
        stream_session=None,
        timestamp_in_video=None,
    ):
        lat = Decimal(str(latitude))
        lng = Decimal(str(longitude))

        with transaction.atomic():
            if cls.is_duplicate(
                defect_type, lat, lng,
                timestamp_in_video=timestamp_in_video,
                road_video=road_video,
            ):
                return None

            try:
                defect = Defect.objects.create(
                    source_type=source_type,
                    defect_type=defect_type,
                    confidence=confidence,
                    bbox=bbox,
                    severity=severity,
                    latitude=lat,
                    longitude=lng,
                    road_image=road_image,
                    road_video=road_video,
                    stream_session=stream_session,
                    timestamp_in_video=timestamp_in_video,
                )
            except IntegrityError:
                return None

            cls._upsert_cluster(defect, lat, lng)
            return defect

    @classmethod
    def is_duplicate(cls, defect_type, lat, lng,
                     timestamp_in_video=None, road_video=None):

        # видео — дубль если тот же тип в пределах 30 секунд в том же видео
        if road_video is not None and timestamp_in_video is not None:
            return Defect.objects.filter(
                defect_type=defect_type,
                road_video=road_video,
                timestamp_in_video__range=(
                    timestamp_in_video - 30,
                    timestamp_in_video + 30,
                ),
            ).exists()

        # фото и стрим — по координатам и времени
        since = timezone.now() - timedelta(minutes=cls.DEDUP_WINDOW_MINUTES)
        return Defect.objects.filter(
            defect_type=defect_type,
            latitude__range=(lat - cls.GEO_THRESHOLD, lat + cls.GEO_THRESHOLD),
            longitude__range=(lng - cls.GEO_THRESHOLD, lng + cls.GEO_THRESHOLD),
            created_at__gte=since,
        ).exists()

    @classmethod
    def _upsert_cluster(cls, defect: Defect, lat: Decimal, lng: Decimal):
        from .models import DefectCluster

        key = cls._cluster_key(defect.defect_type, lat, lng)
        cluster = DefectCluster.objects.filter(cluster_key=key).first()

        if cluster is None:
            DefectCluster.objects.create(
                main_defect=defect,
                cluster_key=key,
                center_latitude=lat,
                center_longitude=lng,
                defect_count=1,
                max_confidence=defect.confidence,
            )
        else:
            cluster.defect_count += 1
            if defect.confidence > cluster.max_confidence:
                cluster.max_confidence = defect.confidence
                cluster.main_defect = defect
            cluster.save(update_fields=[
                "defect_count", "max_confidence", "main_defect", "updated_at"
            ])