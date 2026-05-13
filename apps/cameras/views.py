# views.py
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Camera
from .serializers import CameraSerializer, CameraListSerializer


class CameraViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    GET    /cameras/       — список камер
    POST   /cameras/       — создать камеру
    GET    /cameras/{id}/  — детально
    DELETE /cameras/{id}/  — удалить
    """

    queryset = Camera.objects.all().order_by("name")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return CameraListSerializer
        return CameraSerializer