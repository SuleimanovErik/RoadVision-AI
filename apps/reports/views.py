from rest_framework.views import APIView
from rest_framework.response import Response


# Create your views here.

class GenerateReportView(APIView):
    def get(self, request):
        return Response({"message": "Report generated"})