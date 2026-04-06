from django.urls import path
from .views import CoreView

urlpatterns = [
    path('', CoreView.as_view()),
]