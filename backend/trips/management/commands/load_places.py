"""Load the US Census places gazetteer into the database."""
import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from trips.geo import clean_name, place_key
from trips.models import Place


class Command(BaseCommand):
    """Import data/us_places.txt, keeping one entry per city name and state."""

    help = "Load US places used for location search and log remarks."

    @transaction.atomic
    def handle(self, *args, **options):
        """Replace all places with the gazetteer contents."""
        Place.objects.all().delete()
        seen, places = set(), []
        with open(settings.DATA_DIR / "us_places.txt", encoding="utf-8") as fh:
            for row in csv.DictReader(fh, delimiter="|"):
                name = clean_name(row["NAME"])
                key = (place_key(name), row["USPS"])
                if key in seen:
                    continue
                seen.add(key)
                places.append(
                    Place(key=key[0], name=name, state=row["USPS"],
                          lat=float(row["INTPTLAT"]), lon=float(row["INTPTLONG"].strip()),
                          area=float(row["ALAND_SQMI"]))
                )
        Place.objects.bulk_create(places)
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(places)} places."))
