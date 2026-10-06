"""HTTP endpoints: plan a trip and search places for autocomplete."""
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .geo import LocationNotFound, search_places
from .routing import RouteNotFound
from .trip import plan_trip


@csrf_exempt
@require_POST
def trip(request):
    """POST /api/trip with current_location, pickup_location, dropoff_location and current_cycle_used."""
    try:
        body = json.loads(request.body or "{}")
        cycle_used = float(body.get("current_cycle_used", 0))
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid JSON or cycle hours."}, status=400)
    fields = ("current_location", "pickup_location", "dropoff_location")
    if not all(body.get(field) for field in fields):
        return JsonResponse({"error": "Current, pickup and drop-off locations are required."}, status=400)
    if not 0 <= cycle_used <= 70:
        return JsonResponse({"error": "Current cycle used must be between 0 and 70 hours."}, status=400)
    try:
        return JsonResponse(plan_trip(*(body[field] for field in fields), cycle_used))
    except LocationNotFound as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except RouteNotFound as exc:
        return JsonResponse({"error": str(exc)}, status=502)


@require_GET
def places(request):
    """GET /api/places?q=dal returns matching "City, ST" names."""
    return JsonResponse({"results": search_places(request.GET.get("q", ""))})
