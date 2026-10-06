/** Stop names and colours, plus formatting helpers for times and durations. */

export const STOP_LABELS = {
  start: "Start",
  pickup: "Pickup",
  dropoff: "Drop-off",
  fuel: "Fuel stop",
  break: "30-minute break",
  rest: "10-hour rest",
  restart: "34-hour restart",
};

/** "11:36 AM" style time from an ISO string. */
export function clockTime(iso) {
  return new Date(iso).toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" });
}

/** "Tue, Oct 6" style date from an ISO string. */
export function shortDate(iso) {
  return new Date(iso).toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
}

/** Hours as "h:mm", for example 7.5 -> "7:30". */
export function hoursMinutes(hours) {
  const minutes = Math.round(hours * 60);
  return `${Math.floor(minutes / 60)}:${String(minutes % 60).padStart(2, "0")}`;
}

/** Hours as a readable duration, for example 10.5 -> "10 h 30 min". */
export function duration(hours) {
  const minutes = Math.round(hours * 60);
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  if (!h) return `${m} min`;
  return m ? `${h} h ${m} min` : `${h} h`;
}

export const STOP_COLORS = {
  start: "#1B2A41",
  pickup: "#1D4F91",
  dropoff: "#C8372D",
  fuel: "#2F7D4F",
  break: "#D9A21B",
  rest: "#6B4FA0",
  restart: "#6B4FA0",
};
