/** Colour key for the stop types that appear on the current trip. */
import { STOP_COLORS, STOP_LABELS } from "../format";

export default function MapLegend({ stops }) {
  const types = Object.keys(STOP_LABELS).filter((type) => stops.some((stop) => stop.type === type));
  return (
    <ul className="map-legend" aria-label="Map key">
      {types.map((type) => (
        <li key={type}>
          <span className="stop-dot" style={{ background: STOP_COLORS[type] }} aria-hidden="true" />
          {STOP_LABELS[type]}
        </li>
      ))}
    </ul>
  );
}
