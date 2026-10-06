"""Tests for the HOS simulator, the daily logs and the API."""
import json
from datetime import date
from unittest import mock

from django.test import SimpleTestCase, TestCase

from .hos import DRIVING, OFF_DUTY, ON_DUTY, SLEEPER, simulate_trip
from .logs import daily_logs
from .models import Place
from .routing import Route


def legs(to_pickup_miles, to_dropoff_miles, mph=50.0):
    """Two route legs driven at a constant speed."""
    return [
        {"miles": to_pickup_miles, "hours": to_pickup_miles / mph},
        {"miles": to_dropoff_miles, "hours": to_dropoff_miles / mph},
    ]


def shifts(events):
    """Driving hours in each shift, where shifts are separated by rests of 10 hours or more."""
    totals, current = [], 0.0
    for event in events:
        if event.status == DRIVING:
            current += event.hours
        elif event.status in (OFF_DUTY, SLEEPER) and event.hours >= 10:
            totals.append(current)
            current = 0.0
    return [t for t in totals + [current] if t > 0]


class SimulatorTests(SimpleTestCase):
    """The simulator must respect every HOS limit."""

    def test_short_trip_needs_no_rest(self):
        events = simulate_trip(legs(50, 200), cycle_used=0)
        self.assertNotIn(SLEEPER, {e.status for e in events})
        notes = [e.note for e in events]
        self.assertIn("Pickup", notes)
        self.assertIn("Drop-off", notes)

    def test_never_drives_more_than_11_hours_per_shift(self):
        events = simulate_trip(legs(100, 2500), cycle_used=0)
        self.assertTrue(all(hours <= 11 + 1e-6 for hours in shifts(events)))

    def test_break_after_8_hours_of_driving(self):
        driving_since_break = 0.0
        for event in simulate_trip(legs(100, 2500), cycle_used=0):
            if event.status == DRIVING:
                driving_since_break += event.hours
                self.assertLessEqual(driving_since_break, 8 + 1e-6)
            elif event.hours >= 0.5:
                driving_since_break = 0.0

    def test_fuel_at_least_every_1000_miles(self):
        events = simulate_trip(legs(0, 2600), cycle_used=0)
        fuel_miles = [e.start_mile for e in events if e.note == "Fuel stop"]
        marks = [0.0] + fuel_miles + [2600.0]
        self.assertTrue(all(b - a <= 1000 + 1e-6 for a, b in zip(marks, marks[1:])))

    def test_restart_when_cycle_runs_out(self):
        events = simulate_trip(legs(100, 1500), cycle_used=65)
        self.assertIn("34-hour restart", [e.note for e in events])
        self.assertTrue(all(e.cycle_used <= 70 + 1e-6 for e in events))

    def test_pickup_and_dropoff_are_one_hour_on_duty(self):
        events = simulate_trip(legs(100, 300), cycle_used=0)
        stops = [e for e in events if e.note in ("Pickup", "Drop-off")]
        self.assertEqual([(e.status, e.hours) for e in stops], [(ON_DUTY, 1), (ON_DUTY, 1)])


class DailyLogTests(SimpleTestCase):
    """Each log sheet covers exactly 24 hours."""

    def test_every_day_totals_24_hours(self):
        events = simulate_trip(legs(100, 2500), cycle_used=10)
        sheets = daily_logs(events, date(2026, 1, 5), ["Somewhere, TX"] * len(events))
        self.assertGreater(len(sheets), 1)
        for sheet in sheets:
            self.assertAlmostEqual(sum(sheet["totals"].values()), 24, places=1)


class TripApiTests(TestCase):
    """End-to-end request with the routing service mocked."""

    def setUp(self):
        for name, lat, lon in (("Alpha", 30.0, -97.0), ("Beta", 30.0, -95.0), ("Gamma", 30.0, -90.0)):
            Place.objects.create(key=name.lower(), name=name, state="TX", lat=lat, lon=lon, area=10)

    def test_trip_returns_logs_and_stops(self):
        coords = [(30.0, -97.0 + i * 0.07) for i in range(101)]
        route = Route(coords, legs(120, 300))
        with mock.patch("trips.trip.get_route", return_value=route):
            response = self.client.post(
                "/api/trip",
                json.dumps({"current_location": "Alpha, TX", "pickup_location": "Beta, TX",
                            "dropoff_location": "Gamma, TX", "current_cycle_used": 5}),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual([s["type"] for s in data["stops"]], ["start", "pickup", "dropoff"])
        self.assertEqual(len(data["logs"]), 1)

    def test_rejects_cycle_hours_out_of_range(self):
        body = {"current_location": "Alpha, TX", "pickup_location": "Beta, TX",
                "dropoff_location": "Gamma, TX", "current_cycle_used": 80}
        response = self.client.post("/api/trip", json.dumps(body), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_place_search(self):
        self.assertEqual(self.client.get("/api/places", {"q": "alp"}).json()["results"], ["Alpha, TX"])
