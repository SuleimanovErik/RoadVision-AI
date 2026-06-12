from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.users.permissions import IsAdmin

from .models import Defect, DefectCluster
from .serializers import (
    DefectSerializer,
    DefectListSerializer,
    DefectUpdateSerializer,
    DefectClusterListSerializer,
    DefectClusterDetailSerializer,
)
from .filters import DefectFilter, DefectClusterFilter
from .services import DefectService


# ====================== ДЕФЕКТЫ ======================

class DefectListView(generics.ListAPIView):
    queryset = Defect.objects.all().order_by("-created_at")
    serializer_class = DefectListSerializer
    permission_classes = [IsAuthenticated]  # Все авторизованные
    filter_backends = [DjangoFilterBackend]
    filterset_class = DefectFilter


class DefectDetailView(generics.RetrieveAPIView):
    queryset = Defect.objects.all()
    serializer_class = DefectSerializer
    permission_classes = [IsAuthenticated]  # Все авторизованные


class DefectUpdateView(APIView):
    permission_classes = [IsAdmin]  # Только Админ

    def patch(self, request, pk):
        try:
            defect = Defect.objects.get(pk=pk)
        except Defect.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = DefectUpdateSerializer(defect, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DefectDeleteView(APIView):
    permission_classes = [IsAdmin]  # Только Админ

    def delete(self, request, pk):
        try:
            defect = Defect.objects.get(pk=pk)
        except Defect.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        defect.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LiveDefectView(APIView):
    permission_classes = [IsAuthenticated]  # Все (для стриминга)

    def post(self, request):
        data = request.data
        required = ["defect_type", "confidence", "bbox", "severity", "latitude", "longitude"]

        for f in required:
            if f not in data:
                return Response({"error": f"missing field {f}"}, status=status.HTTP_400_BAD_REQUEST)

        defect = DefectService.create_defect(
            source_type="STREAM",
            defect_type=data["defect_type"],
            confidence=data["confidence"],
            bbox=data["bbox"],
            severity=data["severity"],
            latitude=data["latitude"],
            longitude=data["longitude"],
        )

        if defect is None:
            return Response({"detail": "duplicate"}, status=200)

        return Response({"detail": "saved"}, status=201)


class ConfirmDefectView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            defect = Defect.objects.get(pk=pk)
        except Defect.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        if defect.is_confirmed:
            return Response({"detail": "Already confirmed"}, status=status.HTTP_400_BAD_REQUEST)

        defect.is_confirmed = True
        defect.confirmed_by = request.user
        defect.confirmed_at = timezone.now()
        defect.save()

        return Response({"detail": "Defect confirmed"}, status=status.HTTP_200_OK)


class RejectDefectView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            defect = Defect.objects.get(pk=pk)
        except Defect.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        if defect.is_rejected:
            return Response({"detail": "Already rejected"}, status=status.HTTP_400_BAD_REQUEST)

        defect.is_rejected = True
        defect.rejected_by = request.user
        defect.rejected_at = timezone.now()
        defect.save()

        return Response({"detail": "Defect rejected"}, status=status.HTTP_200_OK)


# ====================== КЛАСТЕРЫ ======================

class DefectClusterListView(generics.ListAPIView):
    queryset = DefectCluster.objects.select_related("main_defect").order_by("-created_at")
    serializer_class = DefectClusterListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DefectClusterFilter


class DefectClusterDetailView(generics.RetrieveAPIView):
    queryset = DefectCluster.objects.select_related("main_defect")
    serializer_class = DefectClusterDetailSerializer
    permission_classes = [IsAuthenticated]