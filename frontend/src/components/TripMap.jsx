/** Route map with a marker for every stop. */
import { useEffect } from "react";
import { CircleMarker, MapContainer, Polyline, TileLayer, Tooltip, useMap } from "react-leaflet";
import { STOP_COLORS, STOP_LABELS, clockTime, duration, shortDate } from "../format";

const USA_CENTER = [39.5, -98.35];
const IS_TOUCH = window.matchMedia("(pointer: coarse)").matches;

/** Keeps the whole route in view, including when the map is resized (rotation, layout change). */
function FitToRoute({ route }) {
  const map = useMap();
  useEffect(() => {
    if (!route.length) return undefined;
    const fit = () => {
      map.invalidateSize();
      map.fitBounds(route, { padding: [32, 32] });
    };
    const observer = new ResizeObserver(fit);
    observer.observe(map.getContainer());
    return () => observer.disconnect();
  }, [map, route]);
  return null;
}

export default function TripMap({ plan }) {
  return (
    <MapContainer center={USA_CENTER} zoom={4} className="trip-map" zoomSnap={0.25} scrollWheelZoom={false} dragging={!IS_TOUCH}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {plan && (
        <>
          <FitToRoute route={plan.route} />
          <Polyline positions={plan.route} pathOptions={{ color: "#1D4F91", weight: 4, opacity: 0.85 }} />
          {plan.stops.map((stop, i) => (
            <CircleMarker
              key={i}
              center={[stop.lat, stop.lon]}
              radius={stop.type === "pickup" || stop.type === "dropoff" || stop.type === "start" ? 9 : 7}
              pathOptions={{ color: "#fff", weight: 2, fillColor: STOP_COLORS[stop.type], fillOpacity: 1 }}
            >
              <Tooltip>
                <strong>{STOP_LABELS[stop.type]}</strong>
                <br />
                {stop.location}
                <br />
                {shortDate(stop.time)}, {clockTime(stop.time)}
                {stop.hours > 0 && ` for ${duration(stop.hours)}`}
              </Tooltip>
            </CircleMarker>
          ))}
        </>
      )}
    </MapContainer>
  );
}
