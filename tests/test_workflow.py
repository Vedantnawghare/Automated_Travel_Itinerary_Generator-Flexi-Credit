import os
import pytest
from agents.orchestrator import OrchestratorAgent
from memory.sqlite_memory import initialize_db, save_preferences, get_preferences
from workflow.travel_graph import route_after_validation


def test_sqlite_memory_read_write(tmp_path):
    """Verify preference storage and retrieval in SQLite."""
    test_db = str(tmp_path / "test_memory.db")
    initialize_db(test_db)

    save_preferences(
        travel_style="relaxed",
        interests=["beaches", "seafood"],
        avoid=["overcrowded clubs"],
        accommodation_preference="resort",
        transportation_preference="flight",
        notes="Allergic to shellfish",
        user_key="tester",
        db_path=test_db
    )

    retrieved = get_preferences(user_key="tester", db_path=test_db)
    assert retrieved["travel_style"] == "relaxed"
    assert "beaches" in retrieved["interests"]
    assert "overcrowded clubs" in retrieved["avoid"]
    assert retrieved["notes"] == "Allergic to shellfish"


def test_end_to_end_workflow_execution():
    """Verify that the full multi-agent LangGraph workflow executes to completion."""
    orchestrator = OrchestratorAgent()
    user_input = {
        "destination": "Jaipur",
        "origin": "Delhi",
        "duration": 3,
        "travellers": 2,
        "budget": 25000.0,
        "travel_style": "balanced",
        "interests": ["Heritage & Architecture", "Local Street Food"],
        "extra_instructions": "Focus on historic forts",
        "email": "test@example.com"
    }

    final_state = orchestrator.plan_trip(user_input)

    assert "final_response" in final_state
    assert len(final_state["itinerary"]) == 3
    assert final_state["budget_breakdown"]["total"] > 0
    assert len(final_state["execution_trace"]) >= 6  # At least 6 agents executed
    assert "Validation Agent" in [step["agent"] for step in final_state["execution_trace"]]


def test_date_handling_modes():
    """Verify explicit dates vs duration-only modes."""
    orchestrator = OrchestratorAgent()

    # Case A: Explicit dates
    req_dates = {
        "destination": "Goa",
        "origin": "Mumbai",
        "start_date": "2026-11-10",
        "end_date": "2026-11-12",
        "duration": 3,
        "travellers": 2,
        "budget": 30000.0,
    }
    state_a = orchestrator.plan_trip(req_dates)
    assert state_a["itinerary"][0].get("date") == "2026-11-10"
    assert state_a["itinerary"][1].get("date") == "2026-11-11"
    assert state_a["itinerary"][2].get("date") == "2026-11-12"

    # Case B: Duration-only (no calendar dates)
    req_no_dates = {
        "destination": "Goa",
        "origin": "Mumbai",
        "start_date": None,
        "end_date": None,
        "duration": 2,
        "travellers": 1,
        "budget": 20000.0,
    }
    state_b = orchestrator.plan_trip(req_no_dates)
    assert state_b["itinerary"][0].get("date") is None


def test_revision_routing_conditional_edge():
    """Verify that route_after_validation returns 'invalid' when issues exist and revision limit not reached."""
    state_invalid = {
        "validation_result": {"is_valid": False},
        "revision_count": 0,
        "max_revisions": 2
    }
    assert route_after_validation(state_invalid) == "invalid"

    state_valid = {
        "validation_result": {"is_valid": True},
        "revision_count": 0,
        "max_revisions": 2
    }
    assert route_after_validation(state_valid) == "valid"

    # When max revisions reached, force valid to prevent infinite loop
    state_max_revisions = {
        "validation_result": {"is_valid": False},
        "revision_count": 2,
        "max_revisions": 2
    }
    assert route_after_validation(state_max_revisions) == "valid"


def test_end_to_end_revision_trigger():
    """Verify that an over-budget itinerary dynamically routes through Revision Agent."""
    orchestrator = OrchestratorAgent()
    # 2 travellers, 5 days with flight and luxury hotel -> total cost ~₹70,000+, but budget set to ₹22,000
    tight_budget_input = {
        "destination": "Goa",
        "origin": "Mumbai",
        "duration": 5,
        "travellers": 2,
        "budget": 22000.0,
        "travel_style": "luxury",
        "accommodation_preference": "luxury hotel",
        "transportation_preference": "flight",
    }
    final_state = orchestrator.plan_trip(tight_budget_input)

    assert final_state["revision_count"] >= 1
    assert any("Revision Agent" in step["agent"] for step in final_state["execution_trace"])
    # After revision, budget agent scaled it down
    assert final_state["budget_breakdown"]["total"] <= 22000.0

