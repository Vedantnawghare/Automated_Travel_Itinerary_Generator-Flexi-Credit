from typing import Dict, Any, Generator
from workflow.travel_graph import travel_graph, TravelGraphState


class OrchestratorAgent:
    """
    Orchestrator Agent:
    The central coordinator that receives the user's travel request, sets up the state,
    initiates the LangGraph multi-agent execution pipeline, and monitors progress through completion.
    """

    def __init__(self):
        self.graph = travel_graph

    def plan_trip(self, user_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the full multi-agent workflow synchronously from start to final.
        Returns the final populated state.
        """
        initial_state: TravelGraphState = {
            "destination": user_request.get("destination", "Goa"),
            "origin": user_request.get("origin", "Mumbai"),
            "start_date": user_request.get("start_date"),
            "end_date": user_request.get("end_date"),
            "duration": int(user_request.get("duration", 3)),
            "travellers": int(user_request.get("travellers", 2)),
            "budget": float(user_request.get("budget", 30000.0)),
            "currency": user_request.get("currency", "INR"),
            "currency_symbol": user_request.get("currency_symbol", "₹"),
            "interests": user_request.get("interests", ["beaches", "cafes"]),
            "travel_style": user_request.get("travel_style", "balanced"),
            "accommodation_preference": user_request.get("accommodation_preference", "mid-range hotel"),
            "transportation_preference": user_request.get("transportation_preference", "flight / train / cab"),
            "extra_instructions": user_request.get("extra_instructions", ""),
            "email": user_request.get("email"),
            "user_key": user_request.get("user_key", "default_user"),
            "revision_count": 0,
            "max_revisions": 2,
            "execution_trace": [],
        }

        # Run compiled LangGraph state machine
        final_state = self.graph.invoke(initial_state)
        return final_state

    def stream_trip(self, user_request: Dict[str, Any]):
        """
        Stream state updates step-by-step for UI progress rendering.
        Yields (node_name, state_snapshot) at each step.
        """
        initial_state: TravelGraphState = {
            "destination": user_request.get("destination", "Goa"),
            "origin": user_request.get("origin", "Mumbai"),
            "start_date": user_request.get("start_date"),
            "end_date": user_request.get("end_date"),
            "duration": int(user_request.get("duration", 3)),
            "travellers": int(user_request.get("travellers", 2)),
            "budget": float(user_request.get("budget", 30000.0)),
            "currency": user_request.get("currency", "INR"),
            "currency_symbol": user_request.get("currency_symbol", "₹"),
            "interests": user_request.get("interests", ["beaches", "cafes"]),
            "travel_style": user_request.get("travel_style", "balanced"),
            "accommodation_preference": user_request.get("accommodation_preference", "mid-range hotel"),
            "transportation_preference": user_request.get("transportation_preference", "flight / train / cab"),
            "extra_instructions": user_request.get("extra_instructions", ""),
            "email": user_request.get("email"),
            "user_key": user_request.get("user_key", "default_user"),
            "revision_count": 0,
            "max_revisions": 2,
            "execution_trace": [],
        }

        for event in self.graph.stream(initial_state):
            yield event
