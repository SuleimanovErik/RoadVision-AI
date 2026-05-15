from django.urls import path
from .views import DefectListView, LiveDefectView

urlpatterns = [
    path("", DefectListView.as_view()),
    path("live/", LiveDefectView.as_view()),
]