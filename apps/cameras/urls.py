from django.urls import path
from .views import CameraListCreateView, CameraDeleteView

urlpatterns = [
    path('', CameraListCreateView.as_view()),
    path('<int:pk>/', CameraDeleteView.as_view()),
]