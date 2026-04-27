from rest_framework import generics, permissions
from .models import Defect
from .serializers import DefectSerializer


# Create your views here.

class DefectListView(generics.ListAPIView):
    queryset = Defect.objects.all().order_by("-created_at")
    serializer_class = DefectSerializer
    permission_classes = [permissions.IsAuthenticated]
