"""Distances, location lookup and nearest-place names, all offline."""
import re
from functools import lru_cache

import numpy as np

from .models import Place

EARTH_RADIUS_MILES = 3958.8
_SUFFIX = re.compile(
    r"\s+(city and borough|consolidated government|unified government|metropolitan government"
    r"|municipality|borough|village|city|town|cdp)(\s*\(.*\))?$",
    re.IGNORECASE,
)


class LocationNotFound(ValueError):
    """Raised when an input location cannot be resolved."""


def clean_name(name):
    """Remove Census suffixes such as " city" or " CDP" from a place name."""
    return _SUFFIX.sub("", name.strip())


def place_key(name):
    """Lowercase lookup key for a city name, so "St. Louis" and "Saint Louis" match."""
    name = re.sub(r"\bst\b\.?", "saint", clean_name(name).lower())
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", "", name)).strip()


def haversine_miles(lat1, lon1, lat2, lon2):
    """Great-circle distance in miles; works on scalars and numpy arrays."""
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2 * EARTH_RADIUS_MILES * np.arcsin(np.sqrt(a))


def geocode(text):
    """Resolve "City, ST" to (lat, lon, label)."""
    parts = [p.strip() for p in (text or "").split(",")]
    if len(parts) != 2 or not all(parts):
        raise LocationNotFound(f'Use the format "City, ST": got "{text}"')
    place = Place.objects.filter(key=place_key(parts[0]), state=parts[1].upper()).first()
    if place is None:
        raise LocationNotFound(f'Unknown US location: "{text}"')
    return place.lat, place.lon, place.label


def search_places(query, limit=8):
    """Places whose name starts with `query` (optionally "City, ST"), for autocomplete."""
    name, _, state = (query or "").partition(",")
    key = place_key(name)
    if len(key) < 2:
        return []
    places = Place.objects.filter(key__startswith=key)
    if state.strip():
        places = places.filter(state__istartswith=state.strip())
    return [p.label for p in places.order_by("-area", "key")[:limit]]


@lru_cache(maxsize=1)
def _place_table():
    """All places as numpy arrays, loaded once per process."""
    rows = list(Place.objects.values_list("name", "state", "lat", "lon"))
    return rows, np.array([r[2] for r in rows]), np.array([r[3] for r in rows])


def nearest_place(lat, lon):
    """Name of the closest US place to a point, such as "Gilman, IL"."""
    rows, lats, lons = _place_table()
    i = int(np.argmin(haversine_miles(lat, lon, lats, lons)))
    return f"{rows[i][0]}, {rows[i][1]}"
