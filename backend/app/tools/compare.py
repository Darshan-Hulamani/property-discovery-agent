from app.tools.data_loader import format_inr, load_listings
from app.tools.neighbourhood import get_neighbourhood_profile


def compare_properties(property_ids: list[str], criteria: list[str] | None = None) -> dict:
    """Side-by-side comparison of 2–5 properties on stated criteria."""
    if len(property_ids) < 2:
        return {"error": "Provide at least 2 property IDs to compare."}
    if len(property_ids) > 5:
        property_ids = property_ids[:5]

    listings = load_listings()
    compared = []
    for pid in property_ids:
        match = next((p for p in listings if p["id"] == pid), None)
        if not match:
            compared.append({"id": pid, "error": "Not found"})
            continue

        profile = get_neighbourhood_profile(match["city"], match["locality"])
        compared.append(
            {
                "id": match["id"],
                "title": match["title"],
                "locality": match["locality"],
                "city": match["city"],
                "bhk": match["bhk"],
                "price_inr": match["price_inr"],
                "price_display": format_inr(match["price_inr"]),
                "sqft": match["sqft"],
                "price_per_sqft": match["price_per_sqft"],
                "builder": match["builder"],
                "possession": match["possession"],
                "tags": match["tags"],
                "school_score": profile.get("school_score"),
                "safety_score": profile.get("safety_score"),
                "metro_km": profile.get("metro_km"),
            }
        )

    return {
        "criteria": criteria or ["price", "location", "schools", "safety", "metro"],
        "properties": compared,
        "note": "Use this data to explain trade-offs to the buyer.",
    }
