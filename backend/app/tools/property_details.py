from app.tools.data_loader import format_inr, load_listings


def get_property_details(property_id: str) -> dict:
    """Get full details for a single property by ID."""
    listings = load_listings()
    match = next((p for p in listings if p["id"] == property_id), None)
    if not match:
        return {"error": f"Property '{property_id}' not found."}

    return {
        **match,
        "price_display": format_inr(match["price_inr"]),
        "note": "Curated demo dataset — not live marketplace listings.",
    }
