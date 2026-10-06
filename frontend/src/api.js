/** Calls to the Django API. Set VITE_API_URL to the deployed backend URL. */
const BASE_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

/** Plan a trip; resolves to the plan or throws an Error with the server's message. */
export async function planTrip(form) {
  const response = await fetch(`${BASE_URL}/api/trip`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      current_location: form.current,
      pickup_location: form.pickup,
      dropoff_location: form.dropoff,
      current_cycle_used: Number(form.cycleUsed),
    }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || "The planner is unavailable. Try again in a moment.");
  }
  return data;
}

/** Suggest "City, ST" names starting with the given text. */
export async function searchPlaces(query) {
  const response = await fetch(`${BASE_URL}/api/places?q=${encodeURIComponent(query)}`);
  if (!response.ok) return [];
  return (await response.json()).results;
}
