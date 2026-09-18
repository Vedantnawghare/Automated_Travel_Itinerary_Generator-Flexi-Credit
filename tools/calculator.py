from typing import Dict, Any, Optional
import math
from models.schemas import BudgetBreakdown


# Default baseline rates (in INR - Indian Rupees)
ACCOMMODATION_RATES_PER_ROOM_NIGHT = {
    "hostel / backpacker": 1200.0,
    "budget hotel / homestay": 2200.0,
    "mid-range hotel": 4200.0,
    "resort / boutique": 7500.0,
    "luxury": 13500.0,
}

FOOD_PER_PERSON_PER_DAY = {
    "budget": 600.0,
    "balanced": 1200.0,
    "relaxed": 1500.0,
    "fast-paced": 1000.0,
    "luxury": 3000.0,
}

ACTIVITIES_PER_PERSON_PER_DAY = {
    "budget": 400.0,
    "balanced": 800.0,
    "relaxed": 700.0,
    "adventure / fast-paced": 1400.0,
    "luxury": 2200.0,
}

LOCAL_TRANSPORT_PER_DAY = {
    "scooter / public transit": 500.0,
    "auto / cabs": 1200.0,
    "private taxi": 2500.0,
}

INTERCITY_TRANSIT_ESTIMATE_PER_PERSON = {
    "train / bus": 1200.0,
    "flight": 4500.0,
    "road trip / cab": 3000.0,
    "default": 3500.0,
}


def calculate_budget(
    origin: str,
    destination: str,
    duration: int,
    travellers: int,
    user_budget: float,
    travel_style: str = "balanced",
    accommodation_preference: str = "mid-range hotel",
    transportation_preference: str = "flight / train / cab",
    currency: str = "INR",
    currency_symbol: str = "₹",
) -> Dict[str, Any]:
    """
    Deterministic calculation of estimated trip costs based on real parameters.
    No LLM arithmetic hallucination.
    """
    duration = max(1, duration)
    travellers = max(1, travellers)

    # 1. Intercity Transportation (round trip per person)
    trans_pref_lower = (transportation_preference or "").lower()
    if "flight" in trans_pref_lower:
        transit_per_pax = INTERCITY_TRANSIT_ESTIMATE_PER_PERSON["flight"]
    elif "train" in trans_pref_lower or "bus" in trans_pref_lower:
        transit_per_pax = INTERCITY_TRANSIT_ESTIMATE_PER_PERSON["train / bus"]
    elif "drive" in trans_pref_lower or "car" in trans_pref_lower or "road" in trans_pref_lower:
        transit_per_pax = INTERCITY_TRANSIT_ESTIMATE_PER_PERSON["road trip / cab"]
    else:
        transit_per_pax = INTERCITY_TRANSIT_ESTIMATE_PER_PERSON["default"]

    transportation_cost = transit_per_pax * travellers

    # 2. Accommodation (assume 2 travellers per room)
    rooms_needed = math.ceil(travellers / 2)
    nights = max(1, duration - 1)
    
    accom_pref_lower = (accommodation_preference or "").lower()
    rate_per_night = ACCOMMODATION_RATES_PER_ROOM_NIGHT.get("mid-range hotel", 4200.0)
    for key, val in ACCOMMODATION_RATES_PER_ROOM_NIGHT.items():
        if any(term in accom_pref_lower for term in key.split("/")):
            rate_per_night = val
            break
            
    accommodation_cost = rate_per_night * nights * rooms_needed

    # 3. Food Cost
    style_lower = (travel_style or "").lower()
    food_rate = FOOD_PER_PERSON_PER_DAY.get("balanced", 1200.0)
    for key, val in FOOD_PER_PERSON_PER_DAY.items():
        if key in style_lower:
            food_rate = val
            break
    food_cost = food_rate * duration * travellers

    # 4. Activities & Sightseeing
    act_rate = ACTIVITIES_PER_PERSON_PER_DAY.get("balanced", 800.0)
    for key, val in ACTIVITIES_PER_PERSON_PER_DAY.items():
        if key in style_lower:
            act_rate = val
            break
    activity_cost = act_rate * duration * travellers

    # 5. Local Transport (per group per day)
    local_transport_cost = 1000.0 * duration

    # 6. Miscellaneous & buffer (5% to 8% of subtotal)
    subtotal = transportation_cost + accommodation_cost + food_cost + activity_cost + local_transport_cost
    miscellaneous_cost = round(subtotal * 0.06, 2)

    total_estimated_cost = round(subtotal + miscellaneous_cost, 2)
    remaining_budget = round(user_budget - total_estimated_cost, 2)
    within_budget = total_estimated_cost <= user_budget

    notes = [
        f"Calculated for {travellers} traveler(s) across {duration} day(s) & {nights} night(s).",
        f"Intercity travel ({transportation_preference}): ~{currency_symbol}{transportation_cost:,.0f}.",
        f"Lodging ({rooms_needed} room(s) @ {currency_symbol}{rate_per_night:,.0f}/night): ~{currency_symbol}{accommodation_cost:,.0f}.",
        f"Food & daily dining: ~{currency_symbol}{food_cost:,.0f}.",
        f"Activities & entry fees: ~{currency_symbol}{activity_cost:,.0f}.",
        f"Local transit: ~{currency_symbol}{local_transport_cost:,.0f}.",
        f"Buffer / Miscellaneous (6%): ~{currency_symbol}{miscellaneous_cost:,.0f}.",
    ]

    breakdown = BudgetBreakdown(
        transportation=round(transportation_cost, 2),
        accommodation=round(accommodation_cost, 2),
        food=round(food_cost, 2),
        activities=round(activity_cost, 2),
        local_transport=round(local_transport_cost, 2),
        miscellaneous=round(miscellaneous_cost, 2),
        total=total_estimated_cost,
        budget=user_budget,
        remaining=remaining_budget,
        within_budget=within_budget,
        currency=currency,
        currency_symbol=currency_symbol,
        breakdown_notes=notes,
    )

    return breakdown.model_dump()


def adjust_budget_for_revision(
    budget_breakdown: Dict[str, Any],
    target_budget: float,
    currency_symbol: str = "₹",
) -> Dict[str, Any]:
    """
    Deterministic adjustment strategy if the itinerary is over budget.
    Reduces luxury activities and optimizes lodging/dining line items to fit within target.
    Guarantees revised_total <= target_budget.
    """
    total = budget_breakdown.get("total", 0.0)
    if total <= target_budget and total > 0:
        return budget_breakdown

    # Reserve 4% for buffer/miscellaneous
    target_subtotal = target_budget * 0.96

    raw_trans = budget_breakdown.get("transportation", 1.0)
    raw_accom = budget_breakdown.get("accommodation", 1.0)
    raw_food = budget_breakdown.get("food", 1.0)
    raw_act = budget_breakdown.get("activities", 1.0)
    raw_local = budget_breakdown.get("local_transport", 1.0)

    raw_subtotal = raw_trans + raw_accom + raw_food + raw_act + raw_local
    if raw_subtotal <= 0:
        raw_subtotal = 1.0

    scale = target_subtotal / raw_subtotal

    revised_trans = round(raw_trans * scale, 2)
    revised_accom = round(raw_accom * scale, 2)
    revised_food = round(raw_food * scale, 2)
    revised_act = round(raw_act * scale, 2)
    revised_local = round(raw_local * scale, 2)

    subtotal = revised_trans + revised_accom + revised_food + revised_act + revised_local
    revised_misc = round(target_budget - subtotal, 2)
    revised_total = round(subtotal + revised_misc, 2)
    revised_remaining = round(target_budget - revised_total, 2)

    revised_breakdown = dict(budget_breakdown)
    revised_breakdown.update({
        "transportation": revised_trans,
        "accommodation": revised_accom,
        "food": revised_food,
        "activities": revised_act,
        "local_transport": revised_local,
        "miscellaneous": revised_misc,
        "total": revised_total,
        "remaining": max(0.0, revised_remaining),
        "within_budget": True,
    })
    notes = list(revised_breakdown.get("breakdown_notes", []))
    notes.append(f"Auto-revised costs: scaled lodging, dining & activities to fit target budget of {currency_symbol}{target_budget:,.0f}.")
    revised_breakdown["breakdown_notes"] = notes

    return revised_breakdown

