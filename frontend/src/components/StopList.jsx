/** The trip's stops in order, grouped by day: start, pickup, fuel, breaks, rests and drop-off. */
import { STOP_COLORS, STOP_LABELS, clockTime, duration, shortDate } from "../format";

function groupByDay(stops) {
  return stops.reduce((days, stop) => {
    const day = shortDate(stop.time);
    const last = days[days.length - 1];
    if (last && last.day === day) last.stops.push(stop);
    else days.push({ day, stops: [stop] });
    return days;
  }, []);
}

export default function StopList({ stops }) {
  return (
    <div className="stop-days">
      {groupByDay(stops).map(({ day, stops: dayStops }, d) => (
        <section key={day} className="stop-day">
          <h3 className="stop-day-title">
            Day {d + 1} <span>{day}</span>
          </h3>
          <ol className="stop-list">
            {dayStops.map((stop, i) => (
              <li key={i} className="stop">
                <span className="stop-time">{clockTime(stop.time)}</span>
                <span className="stop-dot" style={{ background: STOP_COLORS[stop.type] }} aria-hidden="true" />
                <div>
                  <p className="stop-title">
                    {STOP_LABELS[stop.type]}
                    {stop.hours > 0 && <span className="stop-duration">{duration(stop.hours)}</span>}
                  </p>
                  <p className="stop-meta">{stop.location}</p>
                </div>
              </li>
            ))}
          </ol>
        </section>
      ))}
    </div>
  );
}
