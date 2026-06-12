# apps/cameras/views.py
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.users.permissions import IsOperator

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
    GET    /cameras/       — список камер (Operator + Admin)
    POST   /cameras/       — создать камеру (Operator + Admin)
    GET    /cameras/{id}/  — детально (Operator + Admin)
    DELETE /cameras/{id}/  — удалить (Operator + Admin)
    """

    queryset = Camera.objects.all().order_by("name")
    permission_classes = [IsAuthenticated, IsOperator]   # ← Только Оператор и Админ

    def get_serializer_class(self):
        if self.action == "list":
            return CameraListSerializer
        return CameraSerializer