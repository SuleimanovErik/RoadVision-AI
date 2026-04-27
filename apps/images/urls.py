from django.urls import path
from .views import UploadImageView, UploadVideoView

urlpatterns = [
    path('upload/image/', UploadImageView.as_view()),
    path('upload/video/', UploadVideoView.as_view()),
]