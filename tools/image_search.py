import os
import re
import requests
from typing import Dict, Any, List, Optional

# Reliable, high-resolution fallback photography curated for travel categories
FALLBACK_TRAVEL_IMAGES = [
    {
        "url": "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=1200&q=80",
        "alt": "Scenic coastal vista and wanderlust travel view",
        "photographer": "Unsplash Travel",
    },
    {
        "url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
        "alt": "Tropical beach with turquoise waters and palm trees",
        "photographer": "Unsplash Ocean",
    },
    {
        "url": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1200&q=80",
        "alt": "Historic architecture and scenic heritage square",
        "photographer": "Unsplash Heritage",
    },
    {
        "url": "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=1200&q=80",
        "alt": "Winding road through panoramic mountain scenery",
        "photographer": "Unsplash Adventure",
    },
    {
        "url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80",
        "alt": "Lush national park with waterfall and reflections",
        "photographer": "Unsplash Nature",
    },
]

# In-memory session cache for fast lookup across non-Streamlit contexts / fallback
_MEMORY_IMAGE_CACHE: Dict[str, Dict[str, Any]] = {}


def get_pexels_api_key() -> Optional[str]:
    """Retrieve Pexels API Key from environment or Streamlit secrets."""
    key = os.getenv("PEXELS_API_KEY")
    if key and key.strip() and "your_pexels" not in key.lower():
        return key.strip()
    try:
        import streamlit as st
        if "PEXELS_API_KEY" in st.secrets:
            sec_key = st.secrets["PEXELS_API_KEY"].strip()
            if sec_key and "your_pexels" not in sec_key.lower():
                return sec_key
    except Exception:
        pass
    return None


def is_pexels_configured() -> bool:
    """Check if Pexels API is active and configured with a real key."""
    key = get_pexels_api_key()
    return bool(key)


def get_fallback_image(seed: int = 0) -> Dict[str, Any]:
    """Return a guaranteed, reliable travel fallback image."""
    idx = abs(seed) % len(FALLBACK_TRAVEL_IMAGES)
    item = FALLBACK_TRAVEL_IMAGES[idx]
    return {
        "url": item["url"],
        "alt": item["alt"],
        "photographer": item["photographer"],
        "is_fallback": True,
        "query": "travel",
    }


def _raw_pexels_search(
    query: str,
    orientation: str = "landscape",
    per_page: int = 1,
    timeout: int = 5
) -> Optional[Dict[str, Any]]:
    """Execute raw HTTP request to Pexels Search API."""
    api_key = get_pexels_api_key()
    if not api_key:
        return None

    url = "https://api.pexels.com/v1/search"
    headers = {
        "Authorization": api_key,
        "User-Agent": "TravelAI-ItineraryGenerator/1.0",
    }
    params = {
        "query": query,
        "orientation": orientation,
        "per_page": per_page,
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            photos = data.get("photos", [])
            if photos:
                photo = photos[0]
                src = photo.get("src", {})
                # Prefer large2x or large for crisp quality
                img_url = src.get("large2x") or src.get("large") or src.get("medium")
                if img_url:
                    return {
                        "url": img_url,
                        "alt": photo.get("alt") or f"{query} travel view",
                        "photographer": photo.get("photographer", "Pexels Creator"),
                        "photographer_url": photo.get("photographer_url", "https://www.pexels.com"),
                        "is_fallback": False,
                        "query": query,
                    }
    except Exception:
        # Graceful handling for timeouts, connection drops, rate-limits
        pass

    return None


def search_travel_image(
    query: str,
    orientation: str = "landscape",
    fallback_index: int = 0
) -> Dict[str, Any]:
    """
    Search for a travel image dynamically using Pexels.
    Uses memory caching and falls back gracefully to high-res travel placeholders.
    Guaranteed never to throw an exception or crash the application.
    """
    clean_query = query.strip()
    if not clean_query:
        return get_fallback_image(fallback_index)

    cache_key = f"{clean_query.lower()}_{orientation}"

    # Check in-memory cache first
    if cache_key in _MEMORY_IMAGE_CACHE:
        return _MEMORY_IMAGE_CACHE[cache_key]

    # Attempt Pexels API call if key configured
    result = None
    if is_pexels_configured():
        result = _raw_pexels_search(clean_query, orientation=orientation)
        # If specific landmark query returned nothing, retry with simplified query
        if not result and " " in clean_query:
            simplified = " ".join(clean_query.split()[:2])
            result = _raw_pexels_search(simplified, orientation=orientation)

    if not result:
        result = get_fallback_image(fallback_index)
        result["query"] = clean_query

    # Cache successful or fallback result
    _MEMORY_IMAGE_CACHE[cache_key] = result
    return result


def extract_search_query_for_day(destination: str, day_plan: Dict[str, Any]) -> str:
    """
    Derive a natural image search query from an itinerary day's theme and activities.
    Example:
      Destination: "Goa"
      Theme: "Day 1: North Goa Coastal & Baga Beach Chill"
      Morning: ["Visit Fort Aguada lighthouse and ramparts"]
      Result -> "Fort Aguada Goa" or "Baga Beach Goa"
    """
    dest = (destination or "").strip()
    theme = day_plan.get("theme", "")
    morning = day_plan.get("morning", [])
    afternoon = day_plan.get("afternoon", [])
    evening = day_plan.get("evening", [])

    # First, look for prominent place keywords in theme
    theme_clean = re.sub(r"^Day\s*\d+\s*:\s*", "", theme, flags=re.IGNORECASE)

    # Check morning/afternoon activities for recognizable places (Fort, Beach, Temple, Market, Museum, etc.)
    all_activities = morning + afternoon + evening
    key_terms = [
        "beach", "fort", "palace", "temple", "church", "cathedral", "waterfall",
        "lake", "museum", "sanctuary", "market", "bazaar", "cove", "cliff",
        "tower", "monument", "gardens", "park", "square", "bridge", "promenade"
    ]

    for act in all_activities:
        act_lower = act.lower()
        for term in key_terms:
            if term in act_lower:
                # Extract clean entity: strip leading words like "Visit", "Explore", "Enjoy"
                cleaned = re.sub(r"^(visit|explore|stroll along|discover|head to|walk around|tour)\s+", "", act, flags=re.IGNORECASE)
                # Take first 4-5 words before punctuation or parens
                cleaned = re.split(r"[,;:\(\.\-]", cleaned)[0].strip()
                if len(cleaned) > 3:
                    return f"{cleaned} {dest}".strip()

    # Fallback to theme or general destination
    if theme_clean and len(theme_clean) > 3:
        # Take key phrase
        short_theme = re.split(r"[,;&]", theme_clean)[0].strip()
        return f"{short_theme} {dest}".strip()

    return f"{dest} landmark travel"
