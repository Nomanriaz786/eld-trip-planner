"""App configuration for the trips app."""
from django.apps import AppConfig


class TripsConfig(AppConfig):
    """Trip planning and ELD log generation."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "trips"
