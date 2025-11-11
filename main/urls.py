from django.urls import path
from .views import segment_view, highlight_matches

urlpatterns = [
    path("", segment_view, name="segment"),
    path('highlight/', highlight_matches, name='highlight_matches'),
]

