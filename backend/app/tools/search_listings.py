from app.tools.data_loader import format_inr, load_listings


def search_properties(
    city: str | None = None,
    max_budget_inr: int | None = None,
    min_bhk: int | None = None,
    locality: str | None = None,
    property_type: str | None = None,
    must_have_tags: list[str] | None = None,
    limit: int = 10,
) -> dict:
    """Search curated property listings by buyer criteria."""
    results = load_listings()

    if city:
        city_lower = city.strip().lower()
        if city_lower == "bengaluru":
            city_lower = "bangalore"
        elif city_lower == "bombay":
            city_lower = "mumbai"
            
        results = [p for p in results if p["city"].lower() == city_lower]

    if locality:
        loc_lower = locality.strip().lower()
        results = [p for p in results if loc_lower in p["locality"].lower()]

    if max_budget_inr is not None:
        results = [p for p in results if p["price_inr"] <= max_budget_inr]

    if min_bhk is not None:
        results = [p for p in results if p["bhk"] >= min_bhk]

    if property_type:
        pt_lower = property_type.strip().lower()
        results = [p for p in results if p["property_type"].lower() == pt_lower]

    if must_have_tags:
        tag_set = {t.strip().lower() for t in must_have_tags}
        results = [
            p
            for p in results
            if tag_set.issubset({t.lower() for t in p.get("tags", [])})
        ]

    results = results[: max(1, min(limit, 20))]

    summary = [
        {
            "id": p["id"],
            "title": p["title"],
            "city": p["city"],
            "locality": p["locality"],
            "bhk": p["bhk"],
            "price_inr": p["price_inr"],
            "price_display": format_inr(p["price_inr"]),
            "sqft": p["sqft"],
            "property_type": p["property_type"],
            "builder": p["builder"],
            "possession": p["possession"],
            "tags": p["tags"],
            "lat": p.get("lat"),
            "lng": p.get("lng"),
            "image_url": f"/images/luxury_apartment_1_1783011988895.png" if hash(p["id"]) % 2 == 0 else f"/images/luxury_villa_1_1783012004641.png"
        }
        for p in results
    ]

    return {
        "count": len(summary),
        "properties": summary,
        "note": "Curated demo dataset — not live marketplace listings.",
    }
