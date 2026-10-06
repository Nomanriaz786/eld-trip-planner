"""Database model: US places used for location search and log remarks."""
from django.db import models


class Place(models.Model):
    """A US city or town from the Census gazetteer; `area` (square miles) ranks bigger places first."""

    key = models.CharField(max_length=120, db_index=True)
    name = models.CharField(max_length=120)
    state = models.CharField(max_length=2)
    lat = models.FloatField()
    lon = models.FloatField()
    area = models.FloatField(default=0)

    @property
    def label(self):
        """Display name such as "Dallas, TX"."""
        return f"{self.name}, {self.state}"
