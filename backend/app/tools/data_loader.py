import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def load_listings() -> list[dict]:
    with open(DATA_DIR / "listings.json", encoding="utf-8") as f:
        return json.load(f)


def load_neighbourhoods() -> dict:
    with open(DATA_DIR / "neighbourhoods.json", encoding="utf-8") as f:
        return json.load(f)


def format_inr(amount: int) -> str:
    if amount >= 10000000:
        return f"₹{amount / 10000000:.2f} Cr"
    if amount >= 100000:
        return f"₹{amount / 100000:.1f} L"
    return f"₹{amount:,}"
