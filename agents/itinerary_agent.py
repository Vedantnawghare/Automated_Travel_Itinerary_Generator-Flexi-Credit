import datetime
from typing import Dict, Any, List, Optional
from utils.llm_client import call_groq, clean_json_response, is_groq_configured
from utils.prompts import ITINERARY_BUILDER_SYSTEM_PROMPT


class ItineraryAgent:
    """
    Itinerary Builder Agent:
    Combines research findings, user preferences, duration/dates, and budget limits
    to construct a structured, day-wise travel schedule.
    """

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        destination = state.get("destination", "Goa")
        duration = int(state.get("duration", 3))
        start_date_str = state.get("start_date")
        preferences = state.get("preferences", {})
        budget_breakdown = state.get("budget_breakdown", {})
        research_results = state.get("research_results", [])
        
        # Calculate date sequence if explicit start_date is supplied
        day_dates: List[Optional[str]] = []
        if start_date_str:
            try:
                base_date = datetime.date.fromisoformat(str(start_date_str))
                for i in range(duration):
                    day_dates.append((base_date + datetime.timedelta(days=i)).isoformat())
            except Exception:
                day_dates = [None] * duration
        else:
            day_dates = [None] * duration

        # Prepare summary prompt
        research_snippet = "\n".join([
            f"- {item.get('title', '')}: {item.get('content', '')[:160]}"
            for item in research_results[:4]
        ])

        prompt_input = f"""
Build Day-by-Day Travel Itinerary:
- Destination: {destination}
- Duration: {duration} days
- Explicit Day Dates: {day_dates if any(day_dates) else 'None provided (use Day 1, Day 2 etc.)'}
- Preferred Pace / Style: {preferences.get('travel_style', 'balanced')}
- Morning Start Preference: {preferences.get('morning_preference', 'moderate_start')}
- Target Interests: {preferences.get('interests', [])}
- Avoid / Exclude: {preferences.get('avoid', [])}
- Allocated Activity & Food Budget: INR {budget_breakdown.get('activities', 0) + budget_breakdown.get('food', 0):,.0f}

Recent Verified Research Findings:
{research_snippet}

Please build a day-wise itinerary with morning, afternoon, and evening activities.
"""

        itinerary_data: Dict[str, Any] = {}

        if is_groq_configured():
            try:
                messages = [
                    {"role": "system", "content": ITINERARY_BUILDER_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt_input},
                ]
                response_text = call_groq(messages=messages, json_mode=True, temperature=0.3)
                itinerary_data = clean_json_response(response_text)
            except Exception:
                itinerary_data = self._generate_structured_fallback(
                    destination, duration, day_dates, preferences, budget_breakdown, research_results
                )
        else:
            itinerary_data = self._generate_structured_fallback(
                destination, duration, day_dates, preferences, budget_breakdown, research_results
            )

        days = itinerary_data.get("days", [])
        # Ensure day dates align with requested dates
        for idx, day in enumerate(days):
            if idx < len(day_dates) and day_dates[idx]:
                day["date"] = day_dates[idx]

        state["itinerary"] = days
        state["trip_title"] = itinerary_data.get("trip_title", f"Curated {duration}-Day Journey to {destination}")
        state["trip_overview"] = itinerary_data.get("overview", f"A bespoke {duration}-day experience tailored for {preferences.get('travel_style', 'balanced')} travelers.")

        trace = state.setdefault("execution_trace", [])
        trace.append({
            "agent": "Itinerary Builder Agent",
            "action": f"Constructed day-by-day plan covering {len(days)} days with morning, afternoon, and evening activities.",
            "status": "completed",
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })

        return state

    def _generate_structured_fallback(
        self,
        destination: str,
        duration: int,
        day_dates: List[Optional[str]],
        preferences: Dict[str, Any],
        budget: Dict[str, Any],
        research: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Deterministic, rich fallback itinerary generator when API keys are omitted."""
        dest_clean = destination.strip().title()
        interests = preferences.get("interests", ["sightseeing"])
        style = preferences.get("travel_style", "balanced")

        themes = [
            f"Arrival & {dest_clean} Heritage Walk",
            f"Nature, Coastal Scenery & Cafes",
            f"Local Markets & Cultural Landmarks",
            f"Scenic Viewpoints & Sunset Experience",
            f"Leisure, Artisan Souvenirs & Farewell",
        ]

        days = []
        avg_day_cost = round((budget.get("activities", 3000) + budget.get("food", 4500)) / max(1, duration), 0)

        for d in range(1, duration + 1):
            date_val = day_dates[d - 1] if d - 1 < len(day_dates) else None
            theme_idx = (d - 1) % len(themes)
            
            day_plan = {
                "day": d,
                "date": date_val,
                "theme": f"Day {d}: {themes[theme_idx]}",
                "morning": [
                    f"Visit iconic {dest_clean} landmark and historic district (9:30 AM).",
                    f"Enjoy traditional breakfast at a popular local heritage cafe."
                ],
                "afternoon": [
                    f"Explore scenic viewpoints and leisurely walking promenade.",
                    f"Lunch featuring regional culinary specialties."
                ],
                "evening": [
                    f"Sunset stroll along scenic waterfront or bustling night bazaar.",
                    f"Dinner at an ambient cafe or lively bistro."
                ],
                "estimated_cost": avg_day_cost,
                "notes": f"Paced comfortably for a {style} experience with time for relaxation.",
                "travel_tips": "Use local app-cabs or pre-arranged auto-rickshaws for short transit between spots."
            }
            days.append(day_plan)

        return {
            "trip_title": f"The Ultimate {dest_clean} Getaway ({duration} Days)",
            "overview": f"A personalized travel itinerary for {dest_clean} focusing on {', '.join(interests[:3])} with a {style} pace.",
            "days": days
        }
