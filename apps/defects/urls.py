from django.urls import path
from .views import DefectListView

urlpatterns = [
    path("", DefectListView.as_view(), name="defect-list"),
]