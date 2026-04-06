from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

class CameraListCreateView(APIView):
    def get(self, request):
        return Response({"message": "List cameras"})

    def post(self, request):
        return Response({"message": "Camera created"}, status=status.HTTP_201_CREATED)


class CameraDeleteView(APIView):
    def delete(self, request, pk):
        return Response({"message": f"Camera {pk} deleted"})