from django.urls import path
from .views import DefectsView

urlpatterns = [
    path('', DefectsView.as_view()),
]