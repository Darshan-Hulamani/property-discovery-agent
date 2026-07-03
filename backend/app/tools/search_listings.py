from app.tools.data_loader import format_inr, load_listings
from app.tools.ranking import enrich_property, rank_property


def search_properties(
    city: str | None = None,
    max_budget_inr: int | None = None,
    min_bhk: int | None = None,
    locality: str | None = None,
    property_type: str | None = None,
    possession: str | None = None,
    must_have_tags: list[str] | None = None,
    limit: int = 10,
) -> dict:
    """Search curated property listings by buyer criteria with explainable ranking."""
    candidates = load_listings()

    if city:
        city_lower = city.strip().lower()
        if city_lower == "bengaluru":
            city_lower = "bangalore"
        elif city_lower == "bombay":
            city_lower = "mumbai"
        candidates = [p for p in candidates if p["city"].lower() == city_lower]

    if property_type:
        pt_lower = property_type.strip().lower()
        candidates = [p for p in candidates if p["property_type"].lower() == pt_lower]

    if possession:
        possession_lower = possession.strip().lower().replace("-", " ")
        candidates = [
            p
            for p in candidates
            if possession_lower in p.get("possession", "").lower().replace("-", " ")
        ]

    # Keep a few stretch options so the agent can explain trade-offs instead of
    # returning an empty set when the exact budget is tight.
    if max_budget_inr is not None:
        stretch_budget = int(max_budget_inr * 1.12)
        candidates = [p for p in candidates if p["price_inr"] <= stretch_budget]

    if min_bhk is not None:
        candidates = [p for p in candidates if p["bhk"] >= min_bhk]

    target_count = max(1, min(limit, 20))
    primary_candidates = candidates
    fallback_candidates: list[dict] = []
    if locality:
        loc_lower = locality.strip().lower()
        primary_candidates = [p for p in candidates if loc_lower in p["locality"].lower()]
        if primary_candidates:
            fallback_candidates = [p for p in candidates if p not in primary_candidates]
        else:
            primary_candidates = candidates

    primary_ranked = _rank_candidates(primary_candidates, max_budget_inr, min_bhk, locality, must_have_tags)
    fallback_ranked = _rank_candidates(fallback_candidates, max_budget_inr, min_bhk, locality, must_have_tags)
    results = (primary_ranked + fallback_ranked)[:target_count]

    summary = [
        {
            **_summary_fields(enrich_property(property_item, ranking)),
            "price_display": format_inr(property_item["price_inr"]),
            "image_url": _image_for(property_item),
        }
        for _, property_item, ranking in results
    ]

    return {
        "count": len(summary),
        "properties": summary,
        "ranking_model": "Weighted score: budget 22%, BHK 10%, location 12%, schools 12%, safety 12%, metro 10%, preferences 12%, possession 4%, investment 6%.",
        "note": "Curated demo dataset - not live marketplace listings.",
    }


def _rank_candidates(
    candidates: list[dict],
    max_budget_inr: int | None,
    min_bhk: int | None,
    locality: str | None,
    must_have_tags: list[str] | None,
) -> list[tuple[int, dict, dict]]:
    ranked = []
    for property_item in candidates:
        ranking = rank_property(
            property_item,
            max_budget_inr=max_budget_inr,
            min_bhk=min_bhk,
            locality=locality,
            must_have_tags=must_have_tags,
        )
        ranked.append((ranking["score"], property_item, ranking))

    ranked.sort(key=lambda item: (item[0], -item[1]["price_inr"]), reverse=True)
    return ranked


def _summary_fields(property_item: dict) -> dict:
    allowed = {
        "id",
        "title",
        "city",
        "locality",
        "bhk",
        "price_inr",
        "sqft",
        "property_type",
        "builder",
        "possession",
        "tags",
        "lat",
        "lng",
        "score",
        "score_breakdown",
        "score_reasons",
        "amenities",
        "bathrooms",
        "parking",
        "nearby_metro",
        "investment_score",
        "rental_yield_estimate",
        "ai_summary",
    }
    return {key: property_item.get(key) for key in allowed if key in property_item}


def _image_for(property_item: dict) -> str:
    if property_item.get("property_type") == "villa":
        return "/images/luxury_villa_1_1783012004641.png"
    if "premium" in property_item.get("tags", []):
        return "/images/media__1783008194672.png"
    return "/images/luxury_apartment_1_1783011988895.png"
