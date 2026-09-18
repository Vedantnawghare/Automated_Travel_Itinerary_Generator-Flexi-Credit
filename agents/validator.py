import datetime
from typing import Dict, Any, List
from utils.llm_client import call_groq, clean_json_response, is_groq_configured
from utils.prompts import VALIDATOR_SYSTEM_PROMPT


class ValidatorAgent:
    """
    Validation Agent:
    Performs deterministic and semantic validation on the generated itinerary.
    Checks budget constraints, duration fidelity, density, and preference adherence.
    """

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        duration = int(state.get("duration", 3))
        user_budget = float(state.get("budget", 30000.0))
        budget_breakdown = state.get("budget_breakdown", {})
        itinerary = state.get("itinerary", [])
        preferences = state.get("preferences", {})
        travel_style = preferences.get("travel_style", "balanced")
        avoid_items = preferences.get("avoid", [])

        total_cost = budget_breakdown.get("total", 0.0)

        # Deterministic checks first (ground truth)
        budget_ok = total_cost <= user_budget
        duration_ok = len(itinerary) == duration
        density_ok = True
        preference_ok = True
        issues: List[str] = []
        corrections: List[str] = []

        if not budget_ok:
            diff = total_cost - user_budget
            issues.append(f"Budget exceeded by ₹{diff:,.0f} (Estimated: ₹{total_cost:,.0f} vs Budget: ₹{user_budget:,.0f}).")
            corrections.append(f"Reduce activity or lodging tier, optimize dining spend to save ₹{diff:,.0f}.")

        if not duration_ok:
            issues.append(f"Duration mismatch: Expected {duration} days, but itinerary has {len(itinerary)} days.")
            corrections.append(f"Regenerate itinerary to exactly match {duration} days.")

        # Check daily density against travel style
        for day in itinerary:
            m_len = len(day.get("morning", []))
            a_len = len(day.get("afternoon", []))
            e_len = len(day.get("evening", []))
            total_slots = m_len + a_len + e_len

            if "relaxed" in travel_style.lower() and total_slots > 5:
                density_ok = False
                issues.append(f"Day {day.get('day')}: Schedule has {total_slots} activities, which is too dense for a 'relaxed' travel style.")
                corrections.append(f"Streamline Day {day.get('day')} by keeping at most 1-2 key activities per time slot.")
                break

        # Check avoidances
        for avoid_term in avoid_items:
            term_lower = avoid_term.lower()
            for day in itinerary:
                combined_text = (
                    " ".join(day.get("morning", [])) + " " +
                    " ".join(day.get("afternoon", [])) + " " +
                    " ".join(day.get("evening", []))
                ).lower()
                if term_lower in combined_text and term_lower not in ["rushed schedules"]:
                    preference_ok = False
                    issues.append(f"Itinerary mentions '{avoid_term}', which was explicitly flagged to avoid.")
                    corrections.append(f"Remove or replace activities related to '{avoid_term}'.")
                    break

        is_valid = budget_ok and duration_ok and density_ok and preference_ok

        validation_result = {
            "is_valid": is_valid,
            "budget_ok": budget_ok,
            "duration_ok": duration_ok,
            "preference_ok": preference_ok,
            "density_ok": density_ok,
            "issues": issues,
            "suggested_corrections": corrections,
        }

        state["validation_result"] = validation_result

        status_text = "PASSED" if is_valid else f"FAILED ({len(issues)} issues detected)"
        trace = state.setdefault("execution_trace", [])
        trace.append({
            "agent": "Validation Agent",
            "action": f"Validation status: {status_text}. Budget OK: {budget_ok}, Duration OK: {duration_ok}, Density OK: {density_ok}.",
            "status": "completed" if is_valid else "issues_found",
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })

        return state
