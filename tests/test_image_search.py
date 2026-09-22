import pytest
from unittest.mock import patch, MagicMock
from tools.image_search import (
    search_travel_image,
    get_fallback_image,
    extract_search_query_for_day,
    is_pexels_configured,
    get_pexels_api_key,
    _raw_pexels_search,
    _MEMORY_IMAGE_CACHE,
)


def test_fallback_image_guaranteed():
    """Verify fallback image always returns a valid dictionary structure."""
    fallback = get_fallback_image(seed=0)
    assert "url" in fallback
    assert fallback["url"].startswith("http")
    assert fallback["is_fallback"] is True
    assert "photographer" in fallback

    # Verify seed alternation
    fallback_2 = get_fallback_image(seed=1)
    assert fallback_2["url"] != fallback["url"]


def test_missing_pexels_key_returns_fallback(monkeypatch):
    """When PEXELS_API_KEY is missing, image search should gracefully return fallback."""
    monkeypatch.delenv("PEXELS_API_KEY", raising=False)
    # Clear memory cache for this query
    _MEMORY_IMAGE_CACHE.clear()

    res = search_travel_image("Goa Beach Sunset")
    assert res is not None
    assert res["is_fallback"] is True
    assert res["url"].startswith("http")


def test_empty_query_returns_fallback():
    """Empty or whitespace queries return fallback safely without errors."""
    res = search_travel_image("   ")
    assert res["is_fallback"] is True


def test_caching_behavior():
    """Verify repeated queries return cached results without re-fetching."""
    _MEMORY_IMAGE_CACHE.clear()
    q = "Jaipur Hawa Mahal"
    res1 = search_travel_image(q)
    res2 = search_travel_image(q)
    assert res1["url"] == res2["url"]
    cache_key = f"{q.lower()}_landscape"
    assert cache_key in _MEMORY_IMAGE_CACHE


def test_successful_mocked_pexels_lookup(monkeypatch):
    """Verify that a successful Pexels API response is parsed properly."""
    monkeypatch.setenv("PEXELS_API_KEY", "mock_valid_key_12345")
    _MEMORY_IMAGE_CACHE.clear()

    mock_json = {
        "photos": [
            {
                "src": {
                    "large2x": "https://images.pexels.com/photos/123/pexels-photo-123.jpeg",
                    "large": "https://images.pexels.com/photos/123/pexels-photo-123.jpeg"
                },
                "alt": "Vibrant sunset over Baga Beach",
                "photographer": "Travel Photographer",
                "photographer_url": "https://www.pexels.com/@photographer"
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_json

    with patch("requests.get", return_value=mock_resp):
        res = search_travel_image("Baga Beach Goa")
        assert res["is_fallback"] is False
        assert "pexels.com" in res["url"]
        assert res["photographer"] == "Travel Photographer"
        assert res["alt"] == "Vibrant sunset over Baga Beach"


def test_api_failure_returns_fallback(monkeypatch):
    """Verify that network exceptions or timeouts return fallback without raising."""
    monkeypatch.setenv("PEXELS_API_KEY", "mock_key")
    _MEMORY_IMAGE_CACHE.clear()

    with patch("requests.get", side_effect=Exception("Connection timed out")):
        res = search_travel_image("Paris Eiffel Tower")
        assert res is not None
        assert res["is_fallback"] is True
        assert res["url"].startswith("http")


def test_extract_search_query_from_itinerary_day():
    """Verify dynamic place query extraction from itinerary day structure."""
    day_plan = {
        "theme": "Day 1: North Goa Beaches & Fort Exploration",
        "morning": ["Visit Fort Aguada lighthouse and historical ramparts (9:30 AM)."],
        "afternoon": ["Head to Baga Beach for water sports."],
        "evening": ["Sunset stroll at Calangute Beach."]
    }

    query = extract_search_query_for_day("Goa", day_plan)
    # Should extract a specific landmark like "Fort Aguada" or "Baga Beach" combined with destination
    assert "Goa" in query
    assert any(term in query.lower() for term in ["fort aguada", "baga beach", "calangute"])
