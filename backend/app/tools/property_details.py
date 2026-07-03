from app.tools.data_loader import format_inr, load_listings
from app.tools.ranking import enrich_property


def get_property_details(property_id: str) -> dict:
    """Get enriched details for a single property by ID."""
    listings = load_listings()
    match = next((p for p in listings if p["id"] == property_id), None)
    if not match:
        return {"error": f"Property '{property_id}' not found."}

    enriched = enrich_property(match)
    return {
        **enriched,
        "price_display": format_inr(match["price_inr"]),
        "map": {"lat": match.get("lat"), "lng": match.get("lng")},
        "commute": "Use estimate_commute with this property_id for live driving estimates.",
        "note": "Curated demo dataset - not live marketplace listings.",
    }
