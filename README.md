# ELD Trip Planner

Enter a current location, a pickup, a drop-off and the hours already used in the current cycle. The app returns:

- the route on a map, with every required stop marked
- a list of stops: pickup, drop-off, fuel, 30-minute breaks, 10-hour rests and 34-hour restarts
- one filled-in Driver's Daily Log sheet per day, drawn like the paper form

Built with Django (API) and React + Vite (frontend).

## Hours of service rules applied

Property-carrying driver, 70 hours / 8 days, no adverse driving conditions.

| Rule | Value |
| --- | --- |
| Driving limit | 11 hours per shift |
| Driving window | 14 hours after coming on duty |
| Break | 30 minutes after 8 hours of driving (a pickup, drop-off or fuel stop also counts) |
| Rest between shifts | 10 hours, logged as sleeper berth |
| Cycle | 70 hours on duty in 8 days; a 34-hour restart when the remaining cycle is not enough |
| Fuel | every 1,000 miles, 30 minutes on duty |
| Pickup and drop-off | 1 hour on duty each |

Assumptions: the trip starts at 08:00 on the current day, the driver is off duty from midnight until then, and the hours already used in the cycle all fall inside the 8-day window.

## How it works

1. **Geocoding** (`trips/geo.py`): "City, ST" names are matched against the US Census places gazetteer stored in SQLite, so no geocoding API key is needed. The same table powers autocomplete.
2. **Routing** (`trips/routing.py`): one call to the public OSRM server returns the road route through the three points.
3. **Simulation** (`trips/hos.py`): `TripSimulator` builds the trip as a list of duty-status events. Before each stretch of driving it checks, in order, whether the driver needs a 34-hour restart, a 10-hour rest, a 30-minute break or fuel, then drives as far as the tightest limit allows.
4. **Daily logs** (`trips/logs.py`): the events are cut at midnight into one sheet per day, with duty-status segments, totals that always add up to 24 hours, miles, remarks and the 70-hour recap.
5. **Frontend** (`frontend/src`): the form posts to the API; `TripMap` draws the route and stops with Leaflet and `LogSheet` draws each day as SVG.

## Project structure

```
backend/
  config/            Django settings and URLs
  trips/
    geo.py           place lookup and distances
    routing.py       OSRM route
    hos.py           hours of service simulation
    logs.py          daily log sheets
    trip.py          puts it together for the API
    views.py         POST /api/trip, GET /api/places
    tests.py
  data/us_places.txt US Census places gazetteer
  postman/           Postman collection
frontend/
  src/
    App.jsx
    api.js
    format.js
    components/      TripForm, TripMap, StopList, TripSummary, LogSheet
```

## Run locally

Backend (Python 3.12+):

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py load_places
python manage.py runserver
```

Frontend (Node 20+):

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 and click **Fill in an example**.

Tests:

```bash
cd backend
python manage.py test
```

## API

`POST /api/trip`

```json
{
  "current_location": "Chicago, IL",
  "pickup_location": "Indianapolis, IN",
  "dropoff_location": "Los Angeles, CA",
  "current_cycle_used": 20
}
```

Returns `summary`, `route`, `stops` and `logs`. Unknown places return 400 and routing failures 502.

`GET /api/places?q=dal` returns matching place names for autocomplete.

A Postman collection is in `backend/postman/`.

## Deploy

- **Backend** (Render, Railway or similar): build with `pip install -r requirements.txt && python manage.py migrate && python manage.py load_places`, start with `gunicorn config.wsgi`. Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` (the frontend URL).
- **Frontend** (Vercel): root directory `frontend`, set `VITE_API_URL` to the backend URL.
