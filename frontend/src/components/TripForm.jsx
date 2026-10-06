/** The four trip inputs, with "City, ST" suggestions for the locations. */
import { useEffect, useId, useState } from "react";
import { searchPlaces } from "../api";

const EXAMPLE = { current: "Chicago, IL", pickup: "Indianapolis, IN", dropoff: "Los Angeles, CA", cycleUsed: "20" };

function LocationInput({ label, value, onChange }) {
  const listId = useId();
  const [suggestions, setSuggestions] = useState([]);

  useEffect(() => {
    if (value.trim().length < 2) return undefined;
    const timer = setTimeout(() => searchPlaces(value).then(setSuggestions).catch(() => setSuggestions([])), 200);
    return () => clearTimeout(timer);
  }, [value]);

  return (
    <label className="field">
      <span className="field-label">{label}</span>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        list={listId}
        placeholder="City, ST"
        autoComplete="off"
        required
      />
      <datalist id={listId}>
        {(value.trim().length < 2 ? [] : suggestions).map((name) => (
          <option key={name} value={name} />
        ))}
      </datalist>
    </label>
  );
}

export default function TripForm({ onSubmit, loading }) {
  const [form, setForm] = useState({ current: "", pickup: "", dropoff: "", cycleUsed: "0" });
  const set = (key) => (value) => setForm((f) => ({ ...f, [key]: value }));

  return (
    <form
      className="trip-form"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(form);
      }}
    >
      <LocationInput label="Current location" value={form.current} onChange={set("current")} />
      <LocationInput label="Pickup" value={form.pickup} onChange={set("pickup")} />
      <LocationInput label="Drop-off" value={form.dropoff} onChange={set("dropoff")} />
      <label className="field">
        <span className="field-label">Current cycle used (hours)</span>
        <input
          type="number"
          min="0"
          max="70"
          step="0.25"
          value={form.cycleUsed}
          onChange={(e) => set("cycleUsed")(e.target.value)}
          required
        />
        <span className="field-hint">On-duty hours already used in the last 8 days, out of 70.</span>
      </label>
      <div className="form-actions">
        <button type="submit" className="button-primary" disabled={loading}>
          {loading ? "Planning trip..." : "Plan trip"}
        </button>
        <button type="button" className="button-link" onClick={() => setForm(EXAMPLE)} disabled={loading}>
          Fill in an example
        </button>
      </div>
    </form>
  );
}
