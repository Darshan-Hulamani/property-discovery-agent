from __future__ import annotations

from app.tools.neighbourhood import get_neighbourhood_profile


TAG_ALIASES: dict[str, set[str]] = {
    "affordable": {"budget_friendly"},
    "airport_connectivity": {"airport_nearby"},
    "family_friendly": {"gated", "schools_nearby", "green_campus", "clubhouse"},
    "good_schools": {"schools_nearby"},
    "hospital_nearby": {"hospitals_nearby"},
    "investment": {"premium", "it_hub_nearby", "metro_nearby", "airport_nearby"},
    "it_corridor": {"it_hub_nearby"},
    "low_traffic": {"green_campus", "park_facing"},
    "luxury": {"premium", "lake_view", "clubhouse", "smart_home"},
    "metro": {"metro_nearby"},
    "near_metro": {"metro_nearby"},
    "pet_friendly": {"gated", "green_campus", "park_facing"},
    "rental": {"it_hub_nearby", "metro_nearby", "central"},
    "rental_purpose": {"it_hub_nearby", "metro_nearby", "central"},
    "safe_area": {"gated"},
    "schools": {"schools_nearby"},
}

AMENITY_LABELS = {
    "airport_nearby": "Airport corridor",
    "budget_friendly": "Value pricing",
    "central": "Central location",
    "clubhouse": "Clubhouse",
    "gated": "Gated community",
    "green_campus": "Green campus",
    "hospitals_nearby": "Hospitals nearby",
    "it_hub_nearby": "IT corridor",
    "lake_view": "Lake view",
    "metro_nearby": "Metro access",
    "park_facing": "Park-facing",
    "premium": "Premium segment",
    "river_view": "River view",
    "schools_nearby": "Schools nearby",
    "sea_view": "Sea view",
    "smart_home": "Smart home",
    "swimming_pool": "Swimming pool",
    "township": "Township",
}


def normalize_tag(tag: str) -> str:
    return tag.strip().lower().replace(" ", "_").replace("-", "_")


def expand_tags(tags: list[str] | None) -> set[str]:
    expanded: set[str] = set()
    for tag in tags or []:
        normalized = normalize_tag(tag)
        expanded.add(normalized)
        expanded.update(TAG_ALIASES.get(normalized, set()))
    return expanded


def neighborhood_for(property_item: dict) -> dict:
    profile = get_neighbourhood_profile(property_item["city"], property_item["locality"])
    return {} if "error" in profile else profile


def rank_property(
    property_item: dict,
    *,
    max_budget_inr: int | None = None,
    min_bhk: int | None = None,
    locality: str | None = None,
    must_have_tags: list[str] | None = None,
) -> dict:
    profile = neighborhood_for(property_item)
    listing_tags = {normalize_tag(tag) for tag in property_item.get("tags", [])}
    wanted_tags = expand_tags(must_have_tags)

    if max_budget_inr:
        budget_ratio = property_item["price_inr"] / max_budget_inr
        if budget_ratio <= 0.95:
            budget_score = 100
        elif budget_ratio <= 1:
            budget_score = 88
        elif budget_ratio <= 1.08:
            budget_score = 52
        else:
            budget_score = 18
    else:
        budget_score = 72

    if min_bhk:
        bhk_score = 100 if property_item["bhk"] >= min_bhk else 22
    else:
        bhk_score = 74

    locality_score = 72
    if locality:
        target = locality.strip().lower()
        actual = property_item["locality"].lower()
        locality_score = 100 if target in actual else 42

    school_score = float(profile.get("school_score") or 7.0) * 10
    safety_score = float(profile.get("safety_score") or 7.0) * 10
    metro_km = float(profile.get("metro_km") or 6.0)
    metro_score = max(20, 100 - (metro_km * 12))

    if wanted_tags:
        matched_tags = wanted_tags & listing_tags
        tag_score = 35 + round((len(matched_tags) / len(wanted_tags)) * 65)
    else:
        matched_tags = set()
        tag_score = 72

    possession = property_item.get("possession", "").lower()
    possession_score = 92 if "ready" in possession else 70

    investment_score = 60
    if "premium" in listing_tags:
        investment_score += 10
    if "it_hub_nearby" in listing_tags:
        investment_score += 14
    if "metro_nearby" in listing_tags:
        investment_score += 10
    if property_item.get("price_per_sqft", 0) < 7000:
        investment_score += 6
    investment_score = min(investment_score, 100)

    weighted = {
        "budget": budget_score * 0.22,
        "bhk": bhk_score * 0.10,
        "location": locality_score * 0.12,
        "schools": school_score * 0.12,
        "safety": safety_score * 0.12,
        "metro": metro_score * 0.10,
        "preferences": tag_score * 0.12,
        "possession": possession_score * 0.04,
        "investment": investment_score * 0.06,
    }
    score = round(sum(weighted.values()))

    reasons = []
    if max_budget_inr:
        if property_item["price_inr"] <= max_budget_inr:
            reasons.append("Within stated budget")
        else:
            reasons.append("Above budget, included only as a stretch option")
    if locality_score >= 90:
        reasons.append(f"Strong locality match for {property_item['locality']}")
    if school_score >= 80:
        reasons.append("Strong school ecosystem")
    if safety_score >= 80:
        reasons.append("High neighbourhood safety score")
    if metro_score >= 78:
        reasons.append(f"Metro access within {metro_km:g} km")
    if matched_tags:
        labels = [AMENITY_LABELS.get(tag, tag.replace("_", " ").title()) for tag in sorted(matched_tags)]
        reasons.append("Matches preferences: " + ", ".join(labels[:3]))
    if not reasons:
        reasons.append("Balanced match across price, location, and livability")

    return {
        "score": max(0, min(score, 100)),
        "score_breakdown": {
            "budget": round(budget_score),
            "bhk": round(bhk_score),
            "location": round(locality_score),
            "schools": round(school_score),
            "safety": round(safety_score),
            "metro": round(metro_score),
            "preferences": round(tag_score),
            "possession": round(possession_score),
            "investment": round(investment_score),
        },
        "score_reasons": reasons[:4],
        "neighbourhood": {
            "school_score": profile.get("school_score"),
            "safety_score": profile.get("safety_score"),
            "metro_km": profile.get("metro_km"),
            "amenity_summary": profile.get("amenity_summary"),
            "schools": profile.get("schools", []),
            "highlights": profile.get("highlights", []),
        },
    }


def enrich_property(property_item: dict, ranking: dict | None = None) -> dict:
    profile = neighborhood_for(property_item)
    tags = property_item.get("tags", [])
    amenities = [AMENITY_LABELS.get(normalize_tag(tag), tag.replace("_", " ").title()) for tag in tags]
    ranking_data = ranking or rank_property(property_item)

    return {
        **property_item,
        **ranking_data,
        "bathrooms": property_item.get("bathrooms") or max(1, min(property_item.get("bhk", 1), 4)),
        "floor": property_item.get("floor") or ("Mid floor" if property_item.get("property_type") == "apartment" else "Ground + 1"),
        "parking": property_item.get("parking") or ("2 covered" if property_item.get("bhk", 0) >= 3 else "1 covered"),
        "amenities": property_item.get("amenities") or amenities,
        "nearby_schools": property_item.get("nearby_schools") or profile.get("schools", []),
        "nearby_hospitals": property_item.get("nearby_hospitals")
        or ["Major multi-speciality hospital within 15-25 min"],
        "nearby_metro": property_item.get("nearby_metro")
        or (f"{profile.get('metro_km')} km from nearest metro" if profile.get("metro_km") is not None else None),
        "nearby_parks": property_item.get("nearby_parks") or ["Community green space nearby"],
        "nearby_restaurants": property_item.get("nearby_restaurants") or ["Neighbourhood dining and retail cluster nearby"],
        "ai_summary": property_item.get("ai_summary")
        or f"Best suited for buyers who want {property_item['locality']} access with {', '.join(amenities[:3]).lower()} as key strengths.",
        "pros": property_item.get("pros") or ranking_data.get("score_reasons", [])[:3],
        "cons": property_item.get("cons") or _infer_cons(property_item, profile, ranking_data),
        "investment_score": ranking_data.get("score_breakdown", {}).get("investment"),
        "rental_yield_estimate": property_item.get("rental_yield_estimate") or _rental_yield(property_item),
    }


def _infer_cons(property_item: dict, profile: dict, ranking: dict) -> list[str]:
    cons: list[str] = []
    if property_item.get("price_inr", 0) > 15000000:
        cons.append("Premium ticket size narrows affordability")
    if profile.get("metro_km") and float(profile["metro_km"]) > 3:
        cons.append("Metro access may require a short drive")
    if "under construction" in property_item.get("possession", "").lower():
        cons.append("Possession and handover timelines need diligence")
    if ranking.get("score_breakdown", {}).get("budget", 100) < 60:
        cons.append("May stretch the stated budget")
    return cons or ["Curated demo data should be verified against live inventory"]


def _rental_yield(property_item: dict) -> str:
    tags = {normalize_tag(tag) for tag in property_item.get("tags", [])}
    if "it_hub_nearby" in tags or "central" in tags:
        return "3.8% - 4.6%"
    if "premium" in tags:
        return "3.2% - 4.0%"
    return "3.0% - 3.8%"
