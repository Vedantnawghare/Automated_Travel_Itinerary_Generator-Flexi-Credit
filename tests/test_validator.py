import pytest
from agents.validator import ValidatorAgent


def test_validator_valid_itinerary():
    """Verify that a compliant itinerary passes validation without issues."""
    validator = ValidatorAgent()
    state = {
        "duration": 3,
        "budget": 30000.0,
        "budget_breakdown": {"total": 24000.0},
        "preferences": {
            "travel_style": "balanced",
            "avoid": ["crowded nightclubs"],
            "interests": ["beaches", "cafes"]
        },
        "itinerary": [
            {
                "day": 1,
                "morning": ["Beach walk"],
                "afternoon": ["Cafe lunch"],
                "evening": ["Sunset stroll"],
            },
            {
                "day": 2,
                "morning": ["Historic church"],
                "afternoon": ["Museum tour"],
                "evening": ["Seaside dinner"],
            },
            {
                "day": 3,
                "morning": ["Art gallery"],
                "afternoon": ["Souvenir market"],
                "evening": ["Farewell cafe"],
            }
        ]
    }

    res_state = validator.run(state)
    val = res_state["validation_result"]

    assert val["is_valid"] is True
    assert val["budget_ok"] is True
    assert val["duration_ok"] is True
    assert len(val["issues"]) == 0


def test_validator_budget_overflow():
    """Verify that an over-budget itinerary is flagged as invalid."""
    validator = ValidatorAgent()
    state = {
        "duration": 2,
        "budget": 15000.0,
        "budget_breakdown": {"total": 22000.0},  # Exceeds budget
        "preferences": {"travel_style": "balanced", "avoid": []},
        "itinerary": [{"day": 1}, {"day": 2}]
    }

    res_state = validator.run(state)
    val = res_state["validation_result"]

    assert val["is_valid"] is False
    assert val["budget_ok"] is False
    assert any("Budget exceeded" in issue for issue in val["issues"])


def test_validator_duration_mismatch():
    """Verify that duration discrepancies are caught."""
    validator = ValidatorAgent()
    state = {
        "duration": 4,  # Expected 4 days
        "budget": 50000.0,
        "budget_breakdown": {"total": 25000.0},
        "preferences": {"travel_style": "balanced", "avoid": []},
        "itinerary": [{"day": 1}, {"day": 2}]  # Only 2 days provided
    }

    res_state = validator.run(state)
    val = res_state["validation_result"]

    assert val["is_valid"] is False
    assert val["duration_ok"] is False
    assert any("Duration mismatch" in issue for issue in val["issues"])


def test_validator_density_check_relaxed_style():
    """Verify that excessive activities in relaxed style trigger density flag."""
    validator = ValidatorAgent()
    state = {
        "duration": 1,
        "budget": 30000.0,
        "budget_breakdown": {"total": 10000.0},
        "preferences": {"travel_style": "relaxed", "avoid": []},
        "itinerary": [
            {
                "day": 1,
                "morning": ["Spot 1", "Spot 2", "Spot 3"],
                "afternoon": ["Spot 4", "Spot 5"],
                "evening": ["Spot 6", "Spot 7"]  # Total 7 activities -> too dense
            }
        ]
    }

    res_state = validator.run(state)
    val = res_state["validation_result"]

    assert val["is_valid"] is False
    assert val["density_ok"] is False
