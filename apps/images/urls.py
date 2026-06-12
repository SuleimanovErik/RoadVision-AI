from django.urls import path
from .views import (
    UploadImageView,
    UploadVideoView,
    ImageHistoryView,
    ImageDetailView,
    VideoHistoryView,
    VideoDetailView,
)

urlpatterns = [
    path('upload/image/', UploadImageView.as_view()),
    path('upload/video/', UploadVideoView.as_view()),
    path('images/', ImageHistoryView.as_view()),
    path('images/<int:pk>/', ImageDetailView.as_view()),
    path('videos/', VideoHistoryView.as_view()),
    path('videos/<int:pk>/', VideoDetailView.as_view()),
]