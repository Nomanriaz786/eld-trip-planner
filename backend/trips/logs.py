"""Split the trip's duty-status events into one daily log sheet per day."""
from datetime import timedelta

from .hos import CYCLE_LIMIT_HOURS, DRIVING, OFF_DUTY, ON_DUTY, SLEEPER

STATUSES = (OFF_DUTY, SLEEPER, DRIVING, ON_DUTY)


def daily_logs(events, start_date, locations):
    """
    Build the log sheets.

    `locations[i]` is the place name where event i starts. Each sheet has the line
    segments for the grid, hours per status (always 24 in total), miles driven,
    remarks for every change of duty status, and the 70-hour recap.
    """
    days = int(round(events[-1].end / 24))
    sheets = []
    for day in range(days):
        day_start, day_end = day * 24.0, day * 24.0 + 24.0
        segments, totals, miles, remarks = [], dict.fromkeys(STATUSES, 0.0), 0.0, []
        cycle_used = None
        for event, location in zip(events, locations):
            start, end = max(event.start, day_start), min(event.end, day_end)
            if end <= start:
                continue
            segments.append({"status": event.status, "start": start - day_start, "end": end - day_start})
            totals[event.status] += end - start
            if event.status == DRIVING:
                miles += (event.end_mile - event.start_mile) * (end - start) / event.hours
            if day_start <= event.start < day_end:
                remarks.append({"time": event.start - day_start, "location": location, "note": event.note})
            cycle_used = event.cycle_used
        on_duty_today = totals[DRIVING] + totals[ON_DUTY]
        sheets.append(
            {
                "date": (start_date + timedelta(days=day)).isoformat(),
                "segments": segments,
                "totals": {status: round(hours, 2) for status, hours in totals.items()},
                "miles": round(miles, 1),
                "remarks": remarks,
                "recap": {
                    "on_duty_today": round(on_duty_today, 2),
                    "cycle_used": round(cycle_used, 2),
                    "cycle_available": round(max(CYCLE_LIMIT_HOURS - cycle_used, 0), 2),
                },
            }
        )
    return sheets
