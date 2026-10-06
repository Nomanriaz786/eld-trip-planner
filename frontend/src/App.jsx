/** Trip Log Planner: enter a trip, see the route, the required stops and the daily logs. */
import { useState } from "react";
import { planTrip } from "./api";
import LogSheet from "./components/LogSheet";
import MapLegend from "./components/MapLegend";
import StopList from "./components/StopList";
import TripForm from "./components/TripForm";
import TripMap from "./components/TripMap";
import TripSummary from "./components/TripSummary";

export default function App() {
  const [plan, setPlan] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(form) {
    setLoading(true);
    setError("");
    try {
      setPlan(await planTrip(form));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="masthead">
        <h1>Trip Log Planner</h1>
        <p>Route, required stops and daily logs for a property-carrying driver on the 70-hour / 8-day schedule.</p>
      </header>

      <main className="workspace">
        <section className="panel" aria-label="Trip details">
          <TripForm onSubmit={handleSubmit} loading={loading} />
          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}
          {plan && (
            <>
              <TripSummary summary={plan.summary} logCount={plan.logs.length} />
              <div className="stops">
                <h2 className="section-title">Stops</h2>
                <StopList stops={plan.stops} />
              </div>
            </>
          )}
        </section>

        <section className="map-area" aria-label="Route map" aria-busy={loading}>
          <TripMap plan={plan} />
          {plan && <MapLegend stops={plan.stops} />}
          {loading ? (
            <p className="map-status" role="status">
              <span className="spinner" aria-hidden="true" />
              Planning the route and required stops
            </p>
          ) : (
            !plan && <p className="map-status">Enter a trip to see the route, rest stops and fuel stops.</p>
          )}
        </section>
      </main>

      {plan && (
        <section className="logs" aria-label="Daily logs">
          <div className="logs-header">
            <h2 className="section-title">Daily logs</h2>
            <button type="button" className="button-secondary" onClick={() => window.print()}>
              Print logs
            </button>
          </div>
          <p className="logs-hint">Swipe a sheet sideways to see the whole 24 hours.</p>
          {plan.logs.map((log, i) => (
            <div className="log-frame" key={log.date}>
              <LogSheet log={log} index={i} total={plan.logs.length} />
            </div>
          ))}
        </section>
      )}
    </div>
  );
}
