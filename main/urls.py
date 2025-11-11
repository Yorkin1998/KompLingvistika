from django.urls import path
from .views import segment_view, analyze_view

urlpatterns = [
    path("", segment_view, name="segment"),
    path('highlight/', analyze_view, name='analyze_view'),
]

