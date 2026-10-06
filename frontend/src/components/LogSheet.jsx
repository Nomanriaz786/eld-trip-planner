/** One daily log sheet drawn as SVG, laid out like the paper "Driver's Daily Log" form. */
import { hoursMinutes } from "../format";

const ROWS = [
  { status: "off_duty", label: "1. Off duty" },
  { status: "sleeper_berth", label: "2. Sleeper berth" },
  { status: "driving", label: "3. Driving" },
  { status: "on_duty", label: "4. On duty", sub: "(not driving)" },
];
const WIDTH = 1000;
const GRID_X = 168;
const HOUR_WIDTH = 30;
const GRID_WIDTH = HOUR_WIDTH * 24;
const GRID_Y = 240;
const ROW_HEIGHT = 36;
const GRID_BOTTOM = GRID_Y + ROW_HEIGHT * ROWS.length;
const REMARKS_Y = GRID_BOTTOM + 34;
const RECAP_Y = REMARKS_Y + 170;
const HEIGHT = RECAP_Y + 84;

const x = (hours) => GRID_X + hours * HOUR_WIDTH;
const rowCenter = (status) => GRID_Y + ROWS.findIndex((r) => r.status === status) * ROW_HEIGHT + ROW_HEIGHT / 2;

function hourLabel(hour) {
  if (hour === 0 || hour === 24) return "Midnight";
  if (hour === 12) return "Noon";
  return String(hour % 12);
}

function dutyPath(segments) {
  return segments
    .map((s, i) => `${i ? "L" : "M"}${x(s.start)} ${rowCenter(s.status)} L${x(s.end)} ${rowCenter(s.status)}`)
    .join(" ");
}

function mergeRemarks(remarks) {
  return remarks.reduce((merged, remark) => {
    const last = merged[merged.length - 1];
    if (last && last.location === remark.location && remark.time - last.time <= 1) {
      last.note = `${last.note}, then ${remark.note.toLowerCase()}`;
    } else {
      merged.push({ ...remark });
    }
    return merged;
  }, []);
}

function Field({ x: left, y, width, label, value }) {
  return (
    <g>
      <text x={left} y={y - 6} className="log-value">{value}</text>
      <line x1={left} x2={left + width} y1={y} y2={y} className="log-rule" />
      <text x={left} y={y + 15} className="log-caption">{label}</text>
    </g>
  );
}

export default function LogSheet({ log, index, total }) {
  const [year, month, day] = log.date.split("-");
  const remarks = mergeRemarks(log.remarks);
  const miles = Math.round(log.miles);
  const from = remarks[0]?.location ?? "";
  const to = remarks[remarks.length - 1]?.location ?? from;

  return (
    <svg
      className="log-sheet"
      viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      role="img"
      aria-label={`Driver's daily log for ${log.date}, day ${index + 1} of ${total}`}
    >
      <rect width={WIDTH} height={HEIGHT} className="log-paper" />

      <text x="32" y="52" className="log-title">Driver&apos;s Daily Log</text>
      <text x="32" y="74" className="log-caption">24 hours, day {index + 1} of {total}</text>
      <Field x={560} y={52} width={70} label="Month" value={month} />
      <Field x={650} y={52} width={70} label="Day" value={day} />
      <Field x={740} y={52} width={90} label="Year" value={year} />

      <Field x={32} y={118} width={420} label="From" value={from} />
      <Field x={500} y={118} width={460} label="To" value={to} />

      <rect x="32" y="138" width="190" height="40" className="log-box" />
      <text x="127" y="165" textAnchor="middle" className="log-number">{miles}</text>
      <text x="127" y="194" textAnchor="middle" className="log-caption">Total miles driving today</text>
      <rect x="240" y="138" width="190" height="40" className="log-box" />
      <text x="335" y="165" textAnchor="middle" className="log-number">{miles}</text>
      <text x="335" y="194" textAnchor="middle" className="log-caption">Total mileage today</text>
      <Field x={500} y={160} width={460} label="Name of carrier" value="" />

      <rect x={GRID_X} y={GRID_Y} width={GRID_WIDTH} height={GRID_BOTTOM - GRID_Y} className="log-grid-fill" />
      {Array.from({ length: 25 }, (_, h) => (
        <g key={h}>
          <text x={x(h)} y={GRID_Y - 8} textAnchor="middle" className={h % 12 === 0 ? "log-hour log-hour-major" : "log-hour"}>
            {hourLabel(h)}
          </text>
          <line x1={x(h)} x2={x(h)} y1={GRID_Y} y2={GRID_BOTTOM} className="log-grid-line" />
        </g>
      ))}
      {ROWS.map((row, r) => {
        const top = GRID_Y + r * ROW_HEIGHT;
        return (
          <g key={row.status}>
            <line x1={GRID_X} x2={GRID_X + GRID_WIDTH} y1={top} y2={top} className="log-grid-line" />
            {Array.from({ length: 24 * 4 }, (_, q) =>
              q % 4 ? (
                <line
                  key={q}
                  x1={x(q / 4)}
                  x2={x(q / 4)}
                  y1={top}
                  y2={top + (q % 4 === 2 ? 14 : 8)}
                  className="log-tick"
                />
              ) : null,
            )}
            <text x="32" y={top + 22} className="log-row-label">{row.label}</text>
            {row.sub && <text x="52" y={top + 33} className="log-caption">{row.sub}</text>}
            <text x={GRID_X + GRID_WIDTH + 54} y={top + 23} textAnchor="middle" className="log-number">
              {hoursMinutes(log.totals[row.status])}
            </text>
          </g>
        );
      })}
      <line x1={GRID_X} x2={GRID_X + GRID_WIDTH} y1={GRID_BOTTOM} y2={GRID_BOTTOM} className="log-grid-line" />
      <text x={GRID_X + GRID_WIDTH + 54} y={GRID_Y - 8} textAnchor="middle" className="log-hour">Total hours</text>
      <line x1={GRID_X + GRID_WIDTH + 24} x2={GRID_X + GRID_WIDTH + 84} y1={GRID_BOTTOM + 6} y2={GRID_BOTTOM + 6} className="log-rule" />
      <text x={GRID_X + GRID_WIDTH + 54} y={GRID_BOTTOM + 26} textAnchor="middle" className="log-number">
        {hoursMinutes(Object.values(log.totals).reduce((a, b) => a + b, 0))}
      </text>

      <path d={dutyPath(log.segments)} className="log-duty-line" />

      <text x="32" y={REMARKS_Y + 4} className="log-row-label">Remarks</text>
      {log.remarks.map((remark, i) => (
        <line key={i} x1={x(remark.time)} x2={x(remark.time)} y1={GRID_BOTTOM} y2={REMARKS_Y + 2} className="log-remark-tick" />
      ))}
      {remarks.map((remark, i) => (
        <g key={i}>
          <text
            x={x(remark.time) + 3}
            y={REMARKS_Y + 14}
            transform={`rotate(38 ${x(remark.time) + 3} ${REMARKS_Y + 14})`}
            className="log-remark"
          >
            <tspan className="log-remark-place">{remark.location}</tspan>
            <tspan dx="6">{remark.note}</tspan>
          </text>
        </g>
      ))}

      <line x1="32" x2={WIDTH - 32} y1={RECAP_Y - 18} y2={RECAP_Y - 18} className="log-rule" />
      <text x="32" y={RECAP_Y + 8} className="log-row-label">Recap, 70 hours / 8 days</text>
      <text x="32" y={RECAP_Y + 58} className="log-caption">On duty today (lines 3 and 4)</text>
      <text x="32" y={RECAP_Y + 40} className="log-number">{hoursMinutes(log.recap.on_duty_today)}</text>
      <text x="300" y={RECAP_Y + 58} className="log-caption">Total on duty, last 8 days</text>
      <text x="300" y={RECAP_Y + 40} className="log-number">{hoursMinutes(log.recap.cycle_used)}</text>
      <text x="560" y={RECAP_Y + 58} className="log-caption">Available tomorrow (70 hours minus total)</text>
      <text x="560" y={RECAP_Y + 40} className="log-number">{hoursMinutes(log.recap.cycle_available)}</text>
    </svg>
  );
}
