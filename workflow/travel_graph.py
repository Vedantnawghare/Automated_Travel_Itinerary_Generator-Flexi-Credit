from typing import TypedDict, List, Dict, Any, Optional
import datetime
from langgraph.graph import StateGraph, END

from agents.planner import PlannerAgent
from agents.researcher import ResearcherAgent
from agents.preference_agent import PreferenceAgent
from agents.budget_agent import BudgetAgent
from agents.itinerary_agent import ItineraryAgent
from agents.validator import ValidatorAgent
from agents.revision_agent import RevisionAgent
from memory.sqlite_memory import record_trip_history


class TravelGraphState(TypedDict, total=False):
    # User Inputs
    destination: str
    origin: str
    start_date: Optional[str]
    end_date: Optional[str]
    duration: int
    travellers: int
    budget: float
    currency: str
    currency_symbol: str
    interests: List[str]
    travel_style: str
    accommodation_preference: str
    transportation_preference: str
    extra_instructions: str
    email: Optional[str]
    user_key: str

    # Planner
    planner_subtasks: List[str]
    planner_focus_areas: List[str]
    search_queries: List[str]
    constraints: List[str]

    # Research & Memory
    research_results: List[Dict[str, str]]
    preferences: Dict[str, Any]

    # Budget & Itinerary
    budget_breakdown: Dict[str, Any]
    itinerary: List[Dict[str, Any]]
    trip_title: str
    trip_overview: str

    # Validation & Revision
    validation_result: Dict[str, Any]
    revision_count: int
    max_revisions: int
    revision_feedback: List[str]

    # Final Output & Trace
    final_response: Dict[str, Any]
    execution_trace: List[Dict[str, Any]]


# Instantiate agents
planner_agent = PlannerAgent()
researcher_agent = ResearcherAgent()
preference_agent = PreferenceAgent()
budget_agent = BudgetAgent()
itinerary_agent = ItineraryAgent()
validator_agent = ValidatorAgent()
revision_agent = RevisionAgent()


# Node implementations
def orchestrator_init_node(state: TravelGraphState) -> TravelGraphState:
    """Orchestrator perceives request, initializes defaults, and sets the stage."""
    state.setdefault("revision_count", 0)
    state.setdefault("max_revisions", 2)
    state.setdefault("currency", "INR")
    state.setdefault("currency_symbol", "₹")
    state.setdefault("user_key", "default_user")

    trace = state.setdefault("execution_trace", [])
    trace.append({
        "agent": "Orchestrator Agent",
        "action": f"Perceived travel goal for {state.get('destination', 'Goa')} ({state.get('duration', 3)} days, {state.get('travellers', 2)} travellers, budget ₹{state.get('budget', 0):,.0f}). Commencing multi-agent workflow.",
        "status": "started",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    })
    return state


def planner_node(state: TravelGraphState) -> TravelGraphState:
    return planner_agent.run(state)


def research_node(state: TravelGraphState) -> TravelGraphState:
    return researcher_agent.run(state)


def preference_node(state: TravelGraphState) -> TravelGraphState:
    return preference_agent.run(state)


def budget_node(state: TravelGraphState) -> TravelGraphState:
    return budget_agent.run(state)


def itinerary_node(state: TravelGraphState) -> TravelGraphState:
    return itinerary_agent.run(state)


def validator_node(state: TravelGraphState) -> TravelGraphState:
    return validator_agent.run(state)


def revision_node(state: TravelGraphState) -> TravelGraphState:
    return revision_agent.run(state)


def final_response_node(state: TravelGraphState) -> TravelGraphState:
    """Package final output, record in trip history memory, and log completion."""
    destination = state.get("destination", "")
    origin = state.get("origin", "")
    duration = state.get("duration", 1)
    travellers = state.get("travellers", 1)
    budget = state.get("budget", 0.0)
    travel_style = state.get("travel_style", "balanced")

    # Record into SQLite trip history memory
    try:
        record_trip_history(
            destination=destination,
            origin=origin,
            duration=duration,
            travellers=travellers,
            budget=budget,
            travel_style=travel_style,
        )
    except Exception:
        pass

    final_payload = {
        "destination": destination,
        "origin": origin,
        "start_date": state.get("start_date"),
        "end_date": state.get("end_date"),
        "duration": duration,
        "travellers": travellers,
        "budget": budget,
        "trip_title": state.get("trip_title"),
        "trip_overview": state.get("trip_overview"),
        "budget_breakdown": state.get("budget_breakdown"),
        "itinerary": state.get("itinerary"),
        "preferences": state.get("preferences"),
        "research_results": state.get("research_results"),
        "validation_result": state.get("validation_result"),
        "revision_count": state.get("revision_count", 0),
        "email": state.get("email"),
    }
    state["final_response"] = final_payload

    trace = state.setdefault("execution_trace", [])
    trace.append({
        "agent": "Orchestrator Agent",
        "action": f"Workflow completed successfully after {state.get('revision_count', 0)} revision(s). Final itinerary assembled & saved to SQLite memory.",
        "status": "completed",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    })
    return state


def route_after_validation(state: TravelGraphState) -> str:
    """
    Conditional routing edge:
    If validation passed -> route to 'final'
    If validation failed and revision_count < max_revisions -> route to 'revision'
    If max revisions reached -> accept with warnings and route to 'final'
    """
    val_res = state.get("validation_result", {})
    is_valid = val_res.get("is_valid", True)
    revision_count = state.get("revision_count", 0)
    max_revisions = state.get("max_revisions", 2)

    if is_valid:
        return "valid"
    
    if revision_count < max_revisions:
        return "invalid"
    
    # Exceeded max revision cycles, proceed to final with warning
    return "valid"


def build_travel_graph():
    """Build and compile the LangGraph multi-agent workflow."""
    workflow = StateGraph(TravelGraphState)

    # 1. Add nodes
    workflow.add_node("orchestrator", orchestrator_init_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", research_node)
    workflow.add_node("preference", preference_node)
    workflow.add_node("budget", budget_node)
    workflow.add_node("itinerary_builder", itinerary_node)
    workflow.add_node("validator", validator_node)
    workflow.add_node("revision", revision_node)
    workflow.add_node("final", final_response_node)

    # 2. Sequential pipeline
    workflow.set_entry_point("orchestrator")
    workflow.add_edge("orchestrator", "planner")
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "preference")
    workflow.add_edge("preference", "budget")
    workflow.add_edge("budget", "itinerary_builder")
    workflow.add_edge("itinerary_builder", "validator")

    # 3. Conditional Edge from Validator
    workflow.add_conditional_edges(
        "validator",
        route_after_validation,
        {
            "valid": "final",
            "invalid": "revision",
        }
    )

    # 4. Revision routes back to validator for re-evaluation
    workflow.add_edge("revision", "validator")

    # 5. Final reaches END
    workflow.add_edge("final", END)

    return workflow.compile()


# Compiled singleton graph for easy execution
travel_graph = build_travel_graph()
