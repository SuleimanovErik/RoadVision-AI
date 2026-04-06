from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.

class StartStreamView(APIView):
    def post(self, request):
        return Response({"message": "Stream started"})


class StopStreamView(APIView):
    def post(self, request):
        return Response({"message": "Stream stopped"})