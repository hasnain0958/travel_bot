import re
from typing import List, Optional

INTENTS = {
    "greet": ["hi", "hello", "hey"],
    "goodbye": ["bye", "goodbye", "see you"],
    "plan_trip": ["plan", "trip", "travel", "itinerary"],
    "budget": ["budget", "cost", "price"],
    "dates": ["date", "from", "to", "start", "end", "when"],
    "interests": ["beach","mountain","heritage","food","shopping","adventure","nightlife","temple","desert"],
    "weather": ["weather","temperature","rain"],
    "change": ["change","update","modify"]
}

def classify_intent(text: str) -> str:
    t = text.lower()
    for intent, kws in INTENTS.items():
        if any(kw in t for kw in kws):
            return intent
    return "chitchat"

def extract_destination(text: str, known_places: List[str]) -> Optional[str]:
    lt = text.lower()
    for p in known_places:
        if p.lower() in lt:
            return p
    return None

def extract_budget(text: str) -> Optional[int]:
    # Match numbers like 20000 or 20,000
    m = re.search(r"(\d[\d,]{2,})\s*(inr|rs|₹)?", text.lower())
    if m:
        num = m.group(1).replace(',', '')
        try:
            return int(num)
        except ValueError:
            return None
    return None

def extract_dates(text: str):
    # Very simple date extractor: matches DD/MM or DD/MM/YYYY or DD-MM
    dates = re.findall(r"\b(\d{1,2}[\/\-]\d{1,2}(?:[\/\-]\d{2,4})?)\b", text)
    if len(dates) >= 2:
        return dates[0], dates[1]
    if len(dates) == 1:
        return dates[0], None
    return None, None

def extract_interests(text: str) -> List[str]:
    found = []
    lt = text.lower()
    for k in INTENTS["interests"]:
        if k in lt:
            found.append(k)
    return found