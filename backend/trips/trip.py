"""Plan a trip: geocode, route once, simulate hours of service and build the logs."""
from datetime import date, datetime, time, timedelta

from .geo import geocode, nearest_place
from .hos import DRIVING, ON_DUTY, simulate_trip
from .logs import daily_logs
from .routing import get_route

START_HOUR = 8.0
STOP_TYPES = {
    "Pickup": "pickup",
    "Drop-off": "dropoff",
    "Fuel stop": "fuel",
    "30-minute break": "break",
    "10-hour rest": "rest",
    "34-hour restart": "restart",
}


def plan_trip(current, pickup, dropoff, cycle_used, start_date=None):
    """Return the route, stops, daily logs and a summary for one trip."""
    start_date = start_date or date.today()
    places = [geocode(current), geocode(pickup), geocode(dropoff)]
    route = get_route([(lat, lon) for lat, lon, _ in places])
    events = simulate_trip(route.legs, cycle_used, START_HOUR)

    locations = [nearest_place(*route.point_at(event.start_mile)) for event in events]
    origin = datetime.combine(start_date, time())

    stops = [_stop("start", places[0][2], route.point_at(0), _at(origin, START_HOUR), 0)]
    for event, location in zip(events, locations):
        if event.note in STOP_TYPES:
            stops.append(
                _stop(STOP_TYPES[event.note], location, route.point_at(event.start_mile),
                      _at(origin, event.start), event.hours)
            )

    driving = sum(e.hours for e in events if e.status == DRIVING)
    on_duty = sum(e.hours for e in events if e.status in (DRIVING, ON_DUTY))
    arrival = next(e for e in reversed(events) if e.note == "Drop-off")
    return {
        "locations": {"current": places[0][2], "pickup": places[1][2], "dropoff": places[2][2]},
        "summary": {
            "total_miles": round(route.total_miles, 1),
            "driving_hours": round(driving, 2),
            "on_duty_hours": round(on_duty, 2),
            "trip_hours": round(arrival.end - START_HOUR, 2),
            "start": _at(origin, START_HOUR).isoformat(),
            "finish": _at(origin, arrival.end).isoformat(),
            "days": len({int(e.start // 24) for e in events if e.status in (DRIVING, ON_DUTY)}),
        },
        "route": route.simplified(),
        "stops": stops,
        "logs": daily_logs(events, start_date, locations),
    }


def _at(origin, hours):
    """The datetime `hours` after `origin`, rounded to the minute."""
    return origin + timedelta(minutes=round(hours * 60))


def _stop(kind, location, point, when, hours):
    """A map marker for a stop."""
    return {
        "type": kind,
        "location": location,
        "lat": round(point[0], 5),
        "lon": round(point[1], 5),
        "time": when.isoformat(),
        "hours": round(hours, 2),
    }
