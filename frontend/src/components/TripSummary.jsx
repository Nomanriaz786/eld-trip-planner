/** Headline numbers for a planned trip. */
import { clockTime, duration, shortDate } from "../format";

export default function TripSummary({ summary, logCount }) {
  const facts = [
    ["Distance", `${Math.round(summary.total_miles).toLocaleString()} miles`],
    ["Driving time", duration(summary.driving_hours)],
    ["Arrives", `${shortDate(summary.finish)}, ${clockTime(summary.finish)}`],
    ["Log sheets", String(logCount)],
  ];
  return (
    <dl className="summary">
      {facts.map(([label, value]) => (
        <div key={label}>
          <dt>{label}</dt>
          <dd>{value}</dd>
        </div>
      ))}
    </dl>
  );
}
