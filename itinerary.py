import json, random
from pathlib import Path
from typing import Dict, List

KB_PATH = Path(__file__).parent / "kb" / "destinations.json"

def load_kb() -> Dict:
    with open(KB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def estimate_cost(days: int, lo: int, hi: int, budget_inr: int|None):
    est_lo, est_hi = days*lo, days*hi
    if budget_inr is not None:
        if est_lo <= budget_inr <= est_hi:
            band = "within"
        elif budget_inr < est_lo:
            band = "above"
        else:
            band = "below"
    else:
        band = "unknown"
    return est_lo, est_hi, band

def make_itinerary(dest: str, days: int, interests: List[str]) -> List[str]:
    kb = load_kb().get(dest)
    if not kb:
        return [f"Day {i+1}: Explore the city." for i in range(days)]
    spots = kb.get("top_spots", []).copy()
    random.shuffle(spots)
    plan = []
    for d in range(days):
        picks = spots[d % max(1, len(spots))] if spots else "local sights"
        plan.append(f"Day {d+1}: {picks} + nearby food & photo stops.")
    if interests:
        plan[0] += f" (Focus on: {', '.join(interests)})"
    return plan

def packing_tips(dest: str, month: str) -> List[str]:
    base = ["Comfortable walking shoes", "Power bank", "Refillable water bottle", "Basic medicines"]
    if dest.lower() in ["goa","bangkok","dubai"]:
        base += ["Sunscreen", "Beachwear"]
    if dest.lower() in ["manali"]:
        base += ["Warm layers", "Rain jacket"]
    return base + [f"Carry ID and booking confirmations (Month: {month})"]