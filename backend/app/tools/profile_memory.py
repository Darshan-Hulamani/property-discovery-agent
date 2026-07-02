_session_memories: dict[str, dict] = {}

def get_buyer_profile(session_id: str) -> dict:
    """Helper to retrieve the current profile for a session."""
    return _session_memories.setdefault(session_id, {
        "city": None,
        "max_budget_inr": None,
        "min_bhk": None,
        "locality": None,
        "office_landmark": None,
        "must_have_tags": []
    })

def clear_buyer_profile(session_id: str) -> None:
    """Clear memory on reset."""
    _session_memories.pop(session_id, None)

def update_buyer_profile(
    session_id: str,
    city: str | None = None,
    max_budget_inr: int | None = None,
    min_bhk: int | None = None,
    locality: str | None = None,
    office_landmark: str | None = None,
    must_have_tags: list[str] | None = None,
) -> dict:
    """Updates the persistent buyer preference profile. Call this when the user shares constraints."""
    profile = get_buyer_profile(session_id)
    
    if city is not None:
        profile["city"] = city
    if max_budget_inr is not None:
        profile["max_budget_inr"] = max_budget_inr
    if min_bhk is not None:
        profile["min_bhk"] = min_bhk
    if locality is not None:
        profile["locality"] = locality
    if office_landmark is not None:
        profile["office_landmark"] = office_landmark
    if must_have_tags is not None:
        # Merge tags
        current_tags = set(profile.get("must_have_tags") or [])
        current_tags.update(must_have_tags)
        profile["must_have_tags"] = list(current_tags)
        
    return {
        "status": "profile_updated",
        "current_profile": profile
    }
