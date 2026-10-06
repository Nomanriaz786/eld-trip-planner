"""URL routes for the trips app."""
from django.urls import path

from . import views

urlpatterns = [
    path("trip", views.trip, name="trip"),
    path("places", views.places, name="places"),
]
