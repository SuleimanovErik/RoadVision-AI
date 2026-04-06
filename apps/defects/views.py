from django.shortcuts import render

from drf_yasg.openapi import Response
from rest_framework.views import APIView


# Create your views here.

class DefectsView(APIView):
    def get(self, request):
        return Response({"message": "test"})

