import datetime
from typing import Dict, Any, List
from utils.llm_client import call_groq, clean_json_response, is_groq_configured
from utils.prompts import REVISION_SYSTEM_PROMPT
from tools.calculator import adjust_budget_for_revision


class RevisionAgent:
    """
    Revision Agent:
    Takes the critique and suggested corrections from the Validation Agent,
    adjusts budget allocations, and refines the day-wise itinerary to resolve issues.
    """

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state["revision_count"] = state.get("revision_count", 0) + 1
        rev_count = state["revision_count"]

        validation_result = state.get("validation_result", {})
        issues = validation_result.get("issues", [])
        corrections = validation_result.get("suggested_corrections", [])
        itinerary = state.get("itinerary", [])
        budget_breakdown = state.get("budget_breakdown", {})
        user_budget = float(state.get("budget", 30000.0))
        destination = state.get("destination", "Destination")
        travel_style = state.get("travel_style", "balanced")

        # 1. Recalculate and optimize budget if budget issue detected
        if not validation_result.get("budget_ok", True):
            revised_budget = adjust_budget_for_revision(budget_breakdown, target_budget=user_budget)
            state["budget_breakdown"] = revised_budget

        # 2. Revise itinerary content via LLM or deterministic fallback
        prompt_input = f"""
Itinerary Revision Task (Attempt {rev_count}):
- Destination: {destination}
- Target Budget: INR {user_budget:,.0f}
- Travel Style: {travel_style}
- Issues Flagged by Validation Agent:
{chr(10).join(['* ' + iss for iss in issues])}

- Suggested Corrective Actions:
{chr(10).join(['* ' + corr for corr in corrections])}

Current Itinerary:
{itinerary}

Please return the fully revised, compliant itinerary resolving all flagged issues.
"""

        revised_data: Dict[str, Any] = {}

        if is_groq_configured():
            try:
                messages = [
                    {"role": "system", "content": REVISION_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt_input},
                ]
                response_text = call_groq(messages=messages, json_mode=True, temperature=0.2)
                revised_data = clean_json_response(response_text)
            except Exception:
                revised_data = self._deterministic_revision(itinerary, issues, corrections, user_budget)
        else:
            revised_data = self._deterministic_revision(itinerary, issues, corrections, user_budget)

        revised_days = revised_data.get("days", itinerary)
        state["itinerary"] = revised_days
        state["revision_feedback"] = corrections

        trace = state.setdefault("execution_trace", [])
        trace.append({
            "agent": "Revision Agent",
            "action": f"Executed Revision #{rev_count}: Resolved {len(issues)} issue(s) ({', '.join(issues[:2])}).",
            "status": "completed",
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })

        return state

    def _deterministic_revision(
        self,
        itinerary: List[Dict[str, Any]],
        issues: List[str],
        corrections: List[str],
        target_budget: float
    ) -> Dict[str, Any]:
        """Deterministic revision logic for fallback & testing."""
        revised_days = []
        for day in itinerary:
            d = dict(day)
            # Prune morning / afternoon / evening lists if too dense (> 2 items)
            if len(d.get("morning", [])) > 2:
                d["morning"] = d["morning"][:2]
            if len(d.get("afternoon", [])) > 2:
                d["afternoon"] = d["afternoon"][:2]
            if len(d.get("evening", [])) > 2:
                d["evening"] = d["evening"][:2]
            # Reduce day cost estimate
            d["estimated_cost"] = round(float(d.get("estimated_cost", 2000)) * 0.85, 0)
            d["notes"] = (d.get("notes", "") + " [Revised: relaxed pacing and budget-optimized]").strip()
            revised_days.append(d)

        return {
            "days": revised_days,
            "revision_summary": f"Streamlined schedule density and optimized daily spend."
        }
