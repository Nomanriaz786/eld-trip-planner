"""Hours-of-service simulator for a property-carrying driver on the 70-hour / 8-day schedule."""
from dataclasses import dataclass

OFF_DUTY = "off_duty"
SLEEPER = "sleeper_berth"
DRIVING = "driving"
ON_DUTY = "on_duty"

MAX_DRIVING_HOURS = 11
DUTY_WINDOW_HOURS = 14
BREAK_AFTER_DRIVING_HOURS = 8
BREAK_HOURS = 0.5
DAILY_REST_HOURS = 10
CYCLE_LIMIT_HOURS = 70
RESTART_HOURS = 34
FUEL_EVERY_MILES = 1000
FUEL_STOP_HOURS = 0.5
PICKUP_HOURS = 1
DROPOFF_HOURS = 1
EPSILON = 1e-6


@dataclass
class Event:
    """One period in a single duty status. Times are hours from midnight of the first day."""

    status: str
    start: float
    end: float
    start_mile: float
    end_mile: float
    note: str
    cycle_used: float

    @property
    def hours(self):
        """Length of the event in hours."""
        return self.end - self.start


class TripSimulator:
    """Walks through a trip and records every change of duty status while obeying the HOS limits."""

    def __init__(self, cycle_used):
        self.time = 0.0
        self.mile = 0.0
        self.cycle_used = float(cycle_used)
        self.shift_start = None
        self.driven_in_shift = 0.0
        self.driven_since_break = 0.0
        self.miles_since_fuel = 0.0
        self.events = []

    def _record(self, status, hours, note, miles=0.0):
        """Add an event and update every HOS counter it affects."""
        if hours <= EPSILON:
            return
        if status in (DRIVING, ON_DUTY):
            if self.shift_start is None:
                self.shift_start = self.time
            self.cycle_used += hours
        if status == DRIVING:
            self.driven_in_shift += hours
            self.driven_since_break += hours
            self.miles_since_fuel += miles
        elif hours >= BREAK_HOURS - EPSILON:
            self.driven_since_break = 0.0
        if status in (OFF_DUTY, SLEEPER) and hours >= DAILY_REST_HOURS - EPSILON:
            self.shift_start = None
            self.driven_in_shift = 0.0
        if status in (OFF_DUTY, SLEEPER) and hours >= RESTART_HOURS - EPSILON:
            self.cycle_used = 0.0

        last = self.events[-1] if self.events else None
        if last and last.status == status == DRIVING:
            last.end, last.end_mile, last.cycle_used = self.time + hours, self.mile + miles, self.cycle_used
        else:
            self.events.append(
                Event(status, self.time, self.time + hours, self.mile, self.mile + miles, note, self.cycle_used)
            )
        self.time += hours
        self.mile += miles

    def _window_left(self):
        """Hours left in the 14-hour duty window (a fresh window if no shift has started)."""
        return DUTY_WINDOW_HOURS if self.shift_start is None else DUTY_WINDOW_HOURS - (self.time - self.shift_start)

    def _rest(self, cycle_needed):
        """Take a 34-hour restart if the 70-hour cycle is used up, otherwise a 10-hour rest."""
        if CYCLE_LIMIT_HOURS - self.cycle_used < cycle_needed - EPSILON:
            self._record(OFF_DUTY, RESTART_HOURS, "34-hour restart")
        else:
            self._record(SLEEPER, DAILY_REST_HOURS, "10-hour rest")

    def off_duty(self, hours, note):
        """Off duty for a fixed time."""
        self._record(OFF_DUTY, hours, note)

    def on_duty(self, hours, note):
        """On-duty work (pickup, drop-off); rest first if it would break the window or the cycle."""
        if self._window_left() < hours or CYCLE_LIMIT_HOURS - self.cycle_used < hours:
            self._rest(hours)
        self._record(ON_DUTY, hours, note)

    def drive(self, miles, hours, note):
        """Drive a leg, inserting breaks, fuel stops, daily rests and restarts as the rules require."""
        if miles <= EPSILON:
            return
        speed = miles / hours
        remaining = miles
        while remaining > EPSILON:
            if self.cycle_used >= CYCLE_LIMIT_HOURS - EPSILON:
                self._record(OFF_DUTY, RESTART_HOURS, "34-hour restart")
            elif self.driven_in_shift >= MAX_DRIVING_HOURS - EPSILON or self._window_left() <= EPSILON:
                self._rest(0)
            elif self.driven_since_break >= BREAK_AFTER_DRIVING_HOURS - EPSILON:
                self._record(OFF_DUTY, BREAK_HOURS, "30-minute break")
            elif self.miles_since_fuel >= FUEL_EVERY_MILES - EPSILON:
                self._record(ON_DUTY, FUEL_STOP_HOURS, "Fuel stop")
                self.miles_since_fuel = 0.0
            else:
                drive_hours = min(
                    remaining / speed,
                    MAX_DRIVING_HOURS - self.driven_in_shift,
                    self._window_left(),
                    BREAK_AFTER_DRIVING_HOURS - self.driven_since_break,
                    (FUEL_EVERY_MILES - self.miles_since_fuel) / speed,
                    CYCLE_LIMIT_HOURS - self.cycle_used,
                )
                self._record(DRIVING, drive_hours, note, drive_hours * speed)
                remaining -= drive_hours * speed

    def finish_day(self):
        """Stay off duty until the end of the current day so the last log sheet is complete."""
        day_end = (int(self.time // 24) + 1) * 24
        self._record(OFF_DUTY, day_end - self.time, "Off duty")


def simulate_trip(legs, cycle_used, start_hour=8.0):
    """
    Simulate current location -> pickup -> drop-off and return the duty-status events.

    The driver is off duty from midnight until `start_hour`, then drives to the pickup,
    spends an hour loading, drives to the drop-off and spends an hour unloading.
    """
    sim = TripSimulator(cycle_used)
    sim.off_duty(start_hour, "Off duty")
    sim.drive(legs[0]["miles"], legs[0]["hours"], "Driving to pickup")
    sim.on_duty(PICKUP_HOURS, "Pickup")
    sim.drive(legs[1]["miles"], legs[1]["hours"], "Driving to drop-off")
    sim.on_duty(DROPOFF_HOURS, "Drop-off")
    sim.finish_day()
    return sim.events
