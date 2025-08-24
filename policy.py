from .state import ConversationState, Turn
from .nlu import classify_intent, extract_destination, extract_budget, extract_dates, extract_interests
from .itinerary import load_kb, make_itinerary, estimate_cost, packing_tips

from datetime import datetime

KB = load_kb()
KNOWN_PLACES = list(KB.keys())

def respond(state: ConversationState, user_text: str) -> ConversationState:
    intent = classify_intent(user_text)
    slots = state.slots

    # Extract entities opportunistically
    dest = extract_destination(user_text, KNOWN_PLACES)
    if dest:
        slots.destination = dest
    bdg = extract_budget(user_text)
    if bdg:
        slots.budget_inr = bdg
    s, e = extract_dates(user_text)
    if s and not slots.start_date:
        slots.start_date = s
    if e and not slots.end_date:
        slots.end_date = e
    for i in extract_interests(user_text):
        if i not in slots.interests:
            slots.interests.append(i)

    # Simple dialogue policy (English responses)
    if intent == "goodbye" or any(w in user_text.lower() for w in ["thank", "thanks"]):
        bot = "Safe travels! If you need more help, just ask. 👋"
        state.phase = "done"
    elif not slots.destination:
        bot = "Where would you like to go? (e.g., Goa, Jaipur, Manali, Bangkok, Dubai)"
    elif not slots.start_date or not slots.end_date:
        bot = "When are you planning to travel? Please provide start and end dates (e.g., 12/10 to 16/10)."
    elif not slots.budget_inr:
        bot = "What is your approximate budget for the trip in INR?"
    else:
        # All required slots collected -> propose itinerary
        def parse_date(x: str, fallback_year: int | None = None) -> datetime:
            x = x.replace('-', '/')
            for fmt in ["%d/%m/%Y", "%d/%m/%y", "%d/%m"]:
                try:
                    dt = datetime.strptime(x, fmt)
                    if fmt == "%d/%m" and fallback_year is not None:
                        dt = dt.replace(year=fallback_year)
                    return dt
                except ValueError:
                    continue
            raise ValueError("Unrecognized date format. Use DD/MM or DD/MM/YYYY")

        try:
            d1 = parse_date(slots.start_date, fallback_year=datetime.now().year)
        except Exception:
            d1 = datetime.now()
        try:
            d2 = parse_date(slots.end_date, fallback_year=d1.year)
        except Exception:
            d2 = d1

        days = max(1, (d2 - d1).days + 1)
        kb = KB.get(slots.destination, {})
        lo, hi = kb.get("avg_daily_cost_inr", [2000, 5000])
        est_lo, est_hi, band = estimate_cost(days, lo, hi, slots.budget_inr)
        plan = make_itinerary(slots.destination, days, slots.interests)
        tips = packing_tips(slots.destination, d1.strftime("%b"))
        band_text = {
            "within": "Looks within your budget ✅",
            "above": "This may exceed your budget — we can make it cheaper ⚠️",
            "below": "This is comfortable within your budget 😊",
            "unknown": "Could not compare budget."
        }.get(band, "")

        bot = (
            f"Great! Here is a plan for {slots.destination} for {days} day(s).\n"
            f"Estimated spend (stay + food + local travel): ₹{est_lo}–₹{est_hi}. {band_text}\n\n"
            + "\n".join(plan)
            + "\n\nPacking tips: " + ", ".join(tips)
            + "\n\nIf you want, I can suggest cheaper hotels, must-try foods, local transport tips, or weather info."
        )
        state.phase = "suggest_itinerary"

    # Save the turn
    state.history.append(Turn(user=user_text, bot=bot))
    return state