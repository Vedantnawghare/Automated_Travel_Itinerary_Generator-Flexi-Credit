import datetime
from typing import Dict, Any
from tools.calculator import calculate_budget, adjust_budget_for_revision


class BudgetAgent:
    """
    Budget Agent:
    Performs deterministic mathematical estimations for all trip cost categories.
    Compares the calculated total against the user budget to detect violations.
    """

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        origin = state.get("origin", "Mumbai")
        destination = state.get("destination", "Goa")
        duration = int(state.get("duration", 3))
        travellers = int(state.get("travellers", 2))
        user_budget = float(state.get("budget", 30000.0))
        travel_style = state.get("travel_style", "balanced")
        
        pref = state.get("preferences", {})
        accom_pref = pref.get("accommodation_preference") or state.get("accommodation_preference", "mid-range hotel")
        trans_pref = pref.get("transportation_preference") or state.get("transportation_preference", "flight / train / cab")

        # If this is a revision cycle and budget was previously flagged, use adjustment logic
        revision_count = state.get("revision_count", 0)
        validation_res = state.get("validation_result") or {}
        
        if revision_count > 0 and not validation_res.get("budget_ok", True):
            # Recalculate and optimize downwards
            current_breakdown = state.get("budget_breakdown", {})
            breakdown = adjust_budget_for_revision(current_breakdown, target_budget=user_budget)
        else:
            breakdown = calculate_budget(
                origin=origin,
                destination=destination,
                duration=duration,
                travellers=travellers,
                user_budget=user_budget,
                travel_style=travel_style,
                accommodation_preference=accom_pref,
                transportation_preference=trans_pref,
                currency=state.get("currency", "INR"),
                currency_symbol=state.get("currency_symbol", "₹"),
            )

        state["budget_breakdown"] = breakdown

        status_msg = "Within Budget" if breakdown.get("within_budget") else "EXCEEDS BUDGET (Flagged for Review)"
        sym = state.get("currency_symbol", "₹")

        trace = state.setdefault("execution_trace", [])
        trace.append({
            "agent": "Budget Agent",
            "action": f"Calculated total estimate: {sym}{breakdown.get('total', 0):,.0f} vs Budget: {sym}{user_budget:,.0f} -> {status_msg}.",
            "status": "completed",
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })

        return state
