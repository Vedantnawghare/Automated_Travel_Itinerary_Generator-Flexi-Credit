import datetime
import json
from typing import Dict, Any
from utils.llm_client import call_groq, clean_json_response, is_groq_configured
from utils.prompts import PLANNER_SYSTEM_PROMPT


class PlannerAgent:
    """
    Planner Agent:
    Perceives the raw travel request, decomposes the goal into subtasks,
    identifies research needs, constraints, and search queries for the Researcher Agent.
    """

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        destination = state.get("destination", "Goa")
        origin = state.get("origin", "Mumbai")
        duration = state.get("duration", 3)
        travellers = state.get("travellers", 2)
        budget = state.get("budget", 25000.0)
        interests = state.get("interests", ["sightseeing"])
        travel_style = state.get("travel_style", "balanced")
        start_date = state.get("start_date")
        end_date = state.get("end_date")

        date_context = f"from {start_date} to {end_date}" if start_date else f"duration: {duration} days"

        user_content = f"""
Plan Decomposition Request:
- Destination: {destination}
- Starting City: {origin}
- Travel Timing: {date_context}
- Number of Travellers: {travellers}
- Total Budget: INR {budget}
- Interests: {', '.join(interests) if isinstance(interests, list) else str(interests)}
- Travel Style: {travel_style}
- Special Instructions: {state.get('extra_instructions', 'None')}
"""

        plan_data: Dict[str, Any] = {}

        if is_groq_configured():
            try:
                messages = [
                    {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ]
                response_text = call_groq(messages=messages, json_mode=True, temperature=0.2)
                plan_data = clean_json_response(response_text)
            except Exception as e:
                plan_data = self._fallback_plan(destination, origin, duration, interests, travel_style, error=str(e))
        else:
            plan_data = self._fallback_plan(destination, origin, duration, interests, travel_style)

        # Update state
        state["planner_subtasks"] = plan_data.get("subtasks", [])
        state["planner_focus_areas"] = plan_data.get("key_focus_areas", [])
        state["search_queries"] = plan_data.get("search_queries", [
            f"top attractions experiences in {destination}",
            f"best restaurants dining cafes {destination}",
            f"travel practicalities {destination}"
        ])
        state["constraints"] = plan_data.get("constraints", [])

        # Trace log
        trace = state.setdefault("execution_trace", [])
        trace.append({
            "agent": "Planner Agent",
            "action": f"Decomposed {duration}-day trip to {destination} into {len(state['planner_subtasks'])} subtasks and {len(state['search_queries'])} research queries.",
            "status": "completed",
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })

        return state

    def _fallback_plan(self, destination: str, origin: str, duration: int, interests: Any, travel_style: str, error: str = "") -> Dict[str, Any]:
        """Deterministic plan decomposition for demo mode or API fallback."""
        int_list = interests if isinstance(interests, list) else [str(interests)]
        return {
            "subtasks": [
                f"1. Conduct web research for top attractions and activities in {destination}.",
                f"2. Retrieve user preferences and merge with past memory.",
                f"3. Calculate itemized travel budget from {origin} to {destination} for {duration} days.",
                f"4. Construct day-wise realistic itinerary aligned with {travel_style} style and interests ({', '.join(int_list)}).",
                f"5. Validate itinerary density, budget limit, and schedule feasibility.",
            ],
            "key_focus_areas": int_list + [travel_style, "local cuisine"],
            "search_queries": [
                f"must visit attractions in {destination}",
                f"best cafes food and evening spots in {destination}",
                f"travel tips and local transit {destination}"
            ],
            "constraints": [
                f"Stay within specified budget.",
                f"Adhere to {travel_style} pace without over-scheduling.",
                f"Pace activities comfortably for {duration} days."
            ],
            "demo_notice": f"Deterministic fallback plan used ({error})" if error else "Demo mode decomposition"
        }
