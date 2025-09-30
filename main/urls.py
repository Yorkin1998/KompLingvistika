from django.urls import path
from .views import segment_view

urlpatterns = [
    path("", segment_view, name="segment"),
]