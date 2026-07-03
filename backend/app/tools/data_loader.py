import json
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


@lru_cache(maxsize=1)
def load_listings() -> list[dict]:
    with open(DATA_DIR / "listings.json", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_neighbourhoods() -> dict:
    with open(DATA_DIR / "neighbourhoods.json", encoding="utf-8") as f:
        return json.load(f)


def format_inr(amount: int) -> str:
    if amount >= 10000000:
        return f"Rs {amount / 10000000:.2f} Cr"
    if amount >= 100000:
        return f"Rs {amount / 100000:.1f} L"
    return f"Rs {amount:,}"
