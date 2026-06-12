from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StreamSessionViewSet

router = DefaultRouter()
router.register(r"streaming", StreamSessionViewSet, basename="streaming")

urlpatterns = [
    path("", include(router.urls)),
]