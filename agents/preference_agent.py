import datetime
from typing import Dict, Any, List
from memory.sqlite_memory import get_preferences, save_preferences
from utils.llm_client import call_groq, clean_json_response, is_groq_configured
from utils.prompts import PREFERENCE_SYSTEM_PROMPT


class PreferenceAgent:
    """
    Preference Agent:
    Retrieves historical user travel preferences from SQLite memory,
    merges them intelligently with current trip selections, and saves updated preferences.
    """

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        user_key = state.get("user_key", "default_user")
        
        # 1. Retrieve past preferences from SQLite memory
        stored_pref = get_preferences(user_key=user_key)
        
        current_interests = state.get("interests", [])
        if isinstance(current_interests, str):
            current_interests = [i.strip() for i in current_interests.split(",") if i.strip()]
            
        current_style = state.get("travel_style", "balanced")
        current_accom = state.get("accommodation_preference", "mid-range hotel")
        current_trans = state.get("transportation_preference", "flight / train / cab")
        extra_notes = state.get("extra_instructions", "")

        # 2. Combine and resolve
        merged_interests = list(set((stored_pref.get("interests") or []) + current_interests))
        stored_avoid = stored_pref.get("avoid") or []

        prompt_input = f"""
Current Travel Submission:
- Interests: {current_interests}
- Travel Style: {current_style}
- Accommodation: {current_accom}
- Transportation: {current_trans}
- Extra Notes: {extra_notes}

Historical User Memory (from SQLite):
- Past Interests: {stored_pref.get('interests')}
- Past Avoidances: {stored_avoid}
- Past Preferred Style: {stored_pref.get('travel_style')}
- Past Lodging: {stored_pref.get('accommodation_preference')}

Task: Synthesize current inputs with historical memory to build an optimal structured Preference Profile.
"""

        profile_data: Dict[str, Any] = {}

        if is_groq_configured():
            try:
                messages = [
                    {"role": "system", "content": PREFERENCE_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt_input},
                ]
                response_text = call_groq(messages=messages, json_mode=True, temperature=0.2)
                profile_data = clean_json_response(response_text)
            except Exception:
                profile_data = self._deterministic_profile(
                    merged_interests, current_style, stored_avoid, current_accom, current_trans, extra_notes
                )
        else:
            profile_data = self._deterministic_profile(
                merged_interests, current_style, stored_avoid, current_accom, current_trans, extra_notes
            )

        # 3. Persist updated preference snapshot to SQLite memory
        try:
            save_preferences(
                travel_style=profile_data.get("travel_style", current_style),
                interests=profile_data.get("interests", merged_interests),
                avoid=profile_data.get("avoid", stored_avoid),
                accommodation_preference=profile_data.get("accommodation_preference", current_accom),
                transportation_preference=profile_data.get("transportation_preference", current_trans),
                notes=extra_notes,
                user_key=user_key
            )
        except Exception:
            pass

        state["preferences"] = profile_data

        trace = state.setdefault("execution_trace", [])
        trace.append({
            "agent": "Preference Agent",
            "action": f"Synthesized user profile ({profile_data.get('travel_style')} style, {len(profile_data.get('interests', []))} interests) & synchronized SQLite memory.",
            "status": "completed",
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })

        return state

    def _deterministic_profile(
        self,
        interests: List[str],
        travel_style: str,
        avoid: List[str],
        accom: str,
        trans: str,
        extra: str
    ) -> Dict[str, Any]:
        """Fallback deterministic profile synthesis."""
        morning_pref = "late_start" if "relaxed" in travel_style.lower() else "moderate_start"
        auto_avoid = list(avoid)
        if "relaxed" in travel_style.lower() and "rushed schedules" not in auto_avoid:
            auto_avoid.append("rushed schedules")

        return {
            "interests": interests if interests else ["sightseeing", "local food"],
            "travel_style": travel_style,
            "avoid": auto_avoid,
            "morning_preference": morning_pref,
            "accommodation_preference": accom,
            "transportation_preference": trans,
            "preference_notes": f"Combined {len(interests)} active interests with SQLite memory history. Priority: {travel_style} pace."
        }
