import os
from functools import lru_cache

import httpx

from app.tools.data_loader import load_listings, load_neighbourhoods

OSRM_BASE = os.getenv("OSRM_BASE_URL", "https://router.project-osrm.org")

CITY_LANDMARKS: dict[str, tuple[float, float]] = {
    "electronic city bangalore": (12.8456, 77.6603),
    "whitefield bangalore": (12.9698, 77.7499),
    "manyata tech park bangalore": (13.0458, 77.6194),
    "koramangala bangalore": (12.9352, 77.6245),
    "mg road bangalore": (12.9750, 77.6063),
    "indiranagar bangalore": (12.9784, 77.6408),
    "hebbal bangalore": (13.0358, 77.5970),
    "marathahalli bangalore": (12.9591, 77.6974),
    "bellandur bangalore": (12.9260, 77.6761),
    "hinjewadi pune": (18.5912, 73.7389),
    "bandra mumbai": (19.0596, 72.8295),
    "andheri mumbai": (19.1136, 72.8697),
    "hitec city hyderabad": (17.4435, 78.3772),
    "gachibowli hyderabad": (17.4401, 78.3489),
}


@lru_cache(maxsize=64)
def _geocode_nominatim(query: str) -> tuple[float, float] | None:
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": query, "format": "json", "limit": 1, "countrycodes": "in"},
                headers={"User-Agent": "PropertyDiscoveryAgent/1.0"},
            )
            resp.raise_for_status()
            data = resp.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None


def _resolve_coords(
    property_id: str | None,
    locality: str | None,
    city: str | None,
    lat: float | None,
    lng: float | None,
) -> tuple[float, float] | None:
    if lat is not None and lng is not None:
        return lat, lng

    if property_id:
        listings = load_listings()
        match = next((p for p in listings if p["id"] == property_id), None)
        if match:
            return match["lat"], match["lng"]

    if locality and city:
        key = f"{city.strip()}/{locality.strip()}"
        neighbourhoods = load_neighbourhoods()
        if key in neighbourhoods:
            listings = load_listings()
            match = next(
                (p for p in listings if p["locality"].lower() == locality.lower() and p["city"].lower() == city.lower()),
                None,
            )
            if match:
                return match["lat"], match["lng"]

    return None


def _resolve_destination(destination: str) -> tuple[float, float] | None:
    dest_key = destination.strip().lower()
    if dest_key in CITY_LANDMARKS:
        return CITY_LANDMARKS[dest_key]

    for key, coords in CITY_LANDMARKS.items():
        if dest_key in key or key in dest_key:
            return coords

    return _geocode_nominatim(destination + ", India")


def estimate_commute(
    destination: str,
    property_id: str | None = None,
    origin_locality: str | None = None,
    origin_city: str | None = None,
    origin_lat: float | None = None,
    origin_lng: float | None = None,
) -> dict:
    """Estimate driving commute from a property/locality to a workplace or landmark (live OSRM routing)."""
    origin = _resolve_coords(property_id, origin_locality, origin_city, origin_lat, origin_lng)
    if not origin:
        return {
            "error": "Could not resolve origin. Provide property_id or origin_locality + origin_city.",
        }

    dest = _resolve_destination(destination)
    if not dest:
        return {"error": f"Could not geocode destination: {destination}"}

    o_lat, o_lng = origin
    d_lat, d_lng = dest

    try:
        with httpx.Client(timeout=15.0) as client:
            url = f"{OSRM_BASE}/route/v1/driving/{o_lng},{o_lat};{d_lng},{d_lat}"
            resp = client.get(url, params={"overview": "false"})
            resp.raise_for_status()
            data = resp.json()

        if data.get("code") != "Ok" or not data.get("routes"):
            return {"error": "OSRM could not compute a route."}

        route = data["routes"][0]
        duration_min = round(route["duration"] / 60, 1)
        distance_km = round(route["distance"] / 1000, 1)

        return {
            "origin": {"lat": o_lat, "lng": o_lng, "locality": origin_locality, "property_id": property_id},
            "destination": destination,
            "duration_minutes": duration_min,
            "distance_km": distance_km,
            "mode": "driving",
            "source": "live OSRM routing",
        }
    except Exception as exc:
        return {"error": f"Commute calculation failed: {exc}"}
