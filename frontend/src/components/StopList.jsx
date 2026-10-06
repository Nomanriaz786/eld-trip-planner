/** The trip's stops in order: start, pickup, fuel, breaks, rests and drop-off. */
import { STOP_COLORS, STOP_LABELS, clockTime, duration, shortDate } from "../format";

export default function StopList({ stops }) {
  return (
    <ol className="stop-list">
      {stops.map((stop, i) => (
        <li key={i} className="stop">
          <span className="stop-dot" style={{ background: STOP_COLORS[stop.type] }} aria-hidden="true" />
          <div>
            <p className="stop-title">
              {STOP_LABELS[stop.type]}
              {stop.hours > 0 && <span className="stop-duration">{duration(stop.hours)}</span>}
            </p>
            <p className="stop-meta">
              {stop.location}, {shortDate(stop.time)} at {clockTime(stop.time)}
            </p>
          </div>
        </li>
      ))}
    </ol>
  );
}
