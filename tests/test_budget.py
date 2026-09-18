import pytest
from tools.calculator import calculate_budget, adjust_budget_for_revision


def test_budget_calculation_structure():
    """Verify budget calculator returns all required keys and positive values."""
    res = calculate_budget(
        origin="Mumbai",
        destination="Goa",
        duration=4,
        travellers=2,
        user_budget=55000.0,
        travel_style="balanced",
        accommodation_preference="mid-range hotel",
        transportation_preference="flight"
    )

    assert "transportation" in res
    assert "accommodation" in res
    assert "food" in res
    assert "activities" in res
    assert "local_transport" in res
    assert "miscellaneous" in res
    assert "total" in res
    assert "remaining" in res
    assert "within_budget" in res

    assert res["transportation"] > 0
    assert res["accommodation"] > 0
    assert res["total"] > 0
    assert res["within_budget"] is True
    assert res["remaining"] == pytest.approx(55000.0 - res["total"], 0.1)



def test_budget_overflow_detection():
    """Verify that within_budget is False when calculated costs exceed low budget."""
    low_budget = 5000.0  # Impossible for 2 people, 4 days with flight & hotel
    res = calculate_budget(
        origin="Mumbai",
        destination="Goa",
        duration=4,
        travellers=2,
        user_budget=low_budget,
        travel_style="luxury",
        accommodation_preference="luxury hotel",
        transportation_preference="flight"
    )

    assert res["within_budget"] is False
    assert res["total"] > low_budget
    assert res["remaining"] < 0


def test_adjust_budget_for_revision():
    """Verify budget revision optimizer scales costs down to match target budget."""
    initial_breakdown = {
        "transportation": 9000.0,
        "accommodation": 16000.0,
        "food": 8000.0,
        "activities": 6000.0,
        "local_transport": 4000.0,
        "miscellaneous": 2500.0,
        "total": 45500.0,
        "within_budget": False,
        "budget": 30000.0,
        "remaining": -15500.0,
        "breakdown_notes": ["Initial estimate"]
    }

    revised = adjust_budget_for_revision(initial_breakdown, target_budget=30000.0)

    assert revised["total"] <= 30000.0
    assert revised["within_budget"] is True
    assert revised["remaining"] >= 0
    assert len(revised["breakdown_notes"]) > 1
