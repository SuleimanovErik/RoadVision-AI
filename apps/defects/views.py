from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from decimal import Decimal
from .models import Defect
from .serializers import DefectSerializer


class DefectListView(generics.ListAPIView):
    queryset = Defect.objects.all().order_by("-created_at")
    serializer_class = DefectSerializer
    permission_classes = [permissions.IsAuthenticated]


class LiveDefectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # Минимальное расстояние в градусах (~5 метров)
    GEO_THRESHOLD = Decimal("0.00005")

    def post(self, request):
        data = request.data
        required = ["defect_type", "confidence", "bbox", "severity", "latitude", "longitude"]
        for field in required:
            if field not in data:
                return Response({"error": f"missing field: {field}"}, status=status.HTTP_400_BAD_REQUEST)

        lat = Decimal(str(data["latitude"]))
        lng = Decimal(str(data["longitude"]))
        defect_type = data["defect_type"]

        # Проверяем нет ли уже такого дефекта рядом
        duplicate = Defect.objects.filter(
            source_type="STREAM",
            defect_type=defect_type,
            latitude__range=(lat - self.GEO_THRESHOLD, lat + self.GEO_THRESHOLD),
            longitude__range=(lng - self.GEO_THRESHOLD, lng + self.GEO_THRESHOLD),
        ).exists()

        if duplicate:
            return Response({"detail": "duplicate"}, status=status.HTTP_200_OK)

        Defect.objects.create(
            source_type="STREAM",
            defect_type=defect_type,
            confidence=data["confidence"],
            bbox=data["bbox"],
            severity=data["severity"],
            latitude=lat,
            longitude=lng,
        )
        return Response({"detail": "saved"}, status=status.HTTP_201_CREATED)