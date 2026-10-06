"""Single-call routing through the free OSRM API, plus positions along the route."""
import numpy as np
import requests
from django.conf import settings

from .geo import haversine_miles

METERS_PER_MILE = 1609.344


class RouteNotFound(RuntimeError):
    """Raised when the routing service cannot return a route."""


class Route:
    """A driving route through several points, with legs and a way to locate any mile on it."""

    def __init__(self, coords, legs):
        self.legs = legs
        self._lat = np.array([c[0] for c in coords])
        self._lon = np.array([c[1] for c in coords])
        steps = haversine_miles(self._lat[:-1], self._lon[:-1], self._lat[1:], self._lon[1:])
        cumulative = np.concatenate([[0.0], np.cumsum(steps)])
        total = sum(leg["miles"] for leg in legs)
        self._miles = cumulative * (total / cumulative[-1]) if cumulative[-1] > 0 else cumulative

    @property
    def total_miles(self):
        """Total route distance in miles."""
        return float(self._miles[-1])

    def point_at(self, mile):
        """(lat, lon) at a given mile from the start of the route."""
        mile = min(max(mile, 0.0), self.total_miles)
        return float(np.interp(mile, self._miles, self._lat)), float(np.interp(mile, self._miles, self._lon))

    def simplified(self, step_miles=2.0):
        """Coordinates about every `step_miles`, small enough to send to the browser."""
        marks = np.searchsorted(self._miles, np.arange(0, self.total_miles, step_miles))
        idx = np.unique(np.append(marks, len(self._miles) - 1))
        return [[round(float(self._lat[i]), 5), round(float(self._lon[i]), 5)] for i in idx]


def get_route(points):
    """Fetch one route through `points` [(lat, lon), ...]; each leg has miles and hours."""
    path = ";".join(f"{lon},{lat}" for lat, lon in points)
    try:
        response = requests.get(
            f"{settings.OSRM_URL}/route/v1/driving/{path}",
            params={"overview": "full", "geometries": "geojson"},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()["routes"][0]
    except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
        raise RouteNotFound("Routing service could not find a route") from exc
    legs = [{"miles": leg["distance"] / METERS_PER_MILE, "hours": leg["duration"] / 3600} for leg in data["legs"]]
    coords = [(lat, lon) for lon, lat in data["geometry"]["coordinates"]]
    return Route(coords, legs)
