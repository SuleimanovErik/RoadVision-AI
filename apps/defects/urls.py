from django.urls import path
from .views import (
    DefectListView,
    DefectDetailView,
    DefectUpdateView,
    DefectDeleteView,
    LiveDefectView,
    ConfirmDefectView,
    RejectDefectView,
    DefectClusterListView,
    DefectClusterDetailView,
)

urlpatterns = [
    path("", DefectListView.as_view(), name="defect-list"),
    path("<int:pk>/", DefectDetailView.as_view(), name="defect-detail"),
    path("<int:pk>/update/", DefectUpdateView.as_view(), name="defect-update"),
    path("<int:pk>/delete/", DefectDeleteView.as_view(), name="defect-delete"),
    path("live/", LiveDefectView.as_view(), name="defect-live"),
    path("<int:pk>/confirm/", ConfirmDefectView.as_view(), name="defect-confirm"),
    path("<int:pk>/reject/", RejectDefectView.as_view(), name="defect-reject"),
    path("clusters/", DefectClusterListView.as_view(), name="cluster-list"),
    path("clusters/<int:pk>/", DefectClusterDetailView.as_view(), name="cluster-detail"),
]