from app.tools.data_loader import load_neighbourhoods


def get_neighbourhood_profile(city: str, locality: str) -> dict:
    """Get curated neighbourhood profile: schools, safety, metro distance, amenities."""
    neighbourhoods = load_neighbourhoods()
    key = f"{city.strip()}/{locality.strip()}"

    exact = neighbourhoods.get(key)
    if exact:
        return {"city": city, "locality": locality, **exact, "note": "Curated neighbourhood profile — not live API data."}

    city_lower = city.strip().lower()
    locality_lower = locality.strip().lower()
    for k, profile in neighbourhoods.items():
        parts = k.split("/")
        if len(parts) == 2 and parts[0].lower() == city_lower and locality_lower in parts[1].lower():
            return {
                "city": parts[0],
                "locality": parts[1],
                **profile,
                "note": "Curated neighbourhood profile — not live API data.",
            }

    return {
        "error": f"No neighbourhood profile found for {locality}, {city}.",
        "available_localities": [
            k.split("/")[1] for k in neighbourhoods if k.lower().startswith(city_lower + "/")
        ],
    }
