from rest_framework import serializers
from .models import Defect, DefectCluster


class DefectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Defect
        fields = "__all__"


class DefectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Defect
        fields = (
            "id",
            "defect_type",
            "severity",
            "latitude",
            "longitude",
            "confidence",
            "source_type",
            "created_at",
        )


class ConfirmDefectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Defect
        fields = ("is_confirmed", "notes")


class DefectClusterListSerializer(serializers.ModelSerializer):
    defect_type = serializers.CharField(source="main_defect.defect_type")
    severity = serializers.CharField(source="main_defect.severity")
    source_type = serializers.CharField(source="main_defect.source_type")
    last_seen = serializers.DateTimeField(source="updated_at")

    class Meta:
        model = DefectCluster
        fields = (
            "id",
            "cluster_key",
            "defect_type",
            "severity",
            "center_latitude",
            "center_longitude",
            "radius_meters",
            "defect_count",
            "max_confidence",
            "source_type",
            "last_seen",
            "created_at",
        )


class DefectClusterDetailSerializer(serializers.ModelSerializer):
    defect_type = serializers.CharField(source="main_defect.defect_type")
    severity = serializers.CharField(source="main_defect.severity")
    source_type = serializers.CharField(source="main_defect.source_type")
    last_seen = serializers.DateTimeField(source="updated_at")
    # все дефекты в этом кластере
    defects = serializers.SerializerMethodField()

    class Meta:
        model = DefectCluster
        fields = (
            "id",
            "cluster_key",
            "defect_type",
            "severity",
            "center_latitude",
            "center_longitude",
            "radius_meters",
            "defect_count",
            "max_confidence",
            "source_type",
            "last_seen",
            "created_at",
            "defects",
        )

    def get_defects(self, obj):
        # все дефекты в радиусе кластера
        from decimal import Decimal
        threshold = Decimal("0.0001")
        qs = Defect.objects.filter(
            defect_type=obj.main_defect.defect_type,
            latitude__range=(
                obj.center_latitude - threshold,
                obj.center_latitude + threshold,
            ),
            longitude__range=(
                obj.center_longitude - threshold,
                obj.center_longitude + threshold,
            ),
        ).order_by("-confidence")
        return DefectListSerializer(qs, many=True).data

class DefectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Defect
        fields = ("defect_type", "severity", "notes")