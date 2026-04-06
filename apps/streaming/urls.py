from django.urls import path
from .views import StartStreamView, StopStreamView

urlpatterns = [
    path('start/', StartStreamView.as_view()),
    path('stop/', StopStreamView.as_view()),
]