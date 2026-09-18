import os
from typing import List, Dict, Any, Optional


def get_tavily_api_key() -> Optional[str]:
    """Retrieve Tavily API Key from environment or Streamlit secrets."""
    key = os.getenv("TAVILY_API_KEY")
    if key:
        return key.strip()
    try:
        import streamlit as st
        if "TAVILY_API_KEY" in st.secrets:
            return st.secrets["TAVILY_API_KEY"].strip()
    except Exception:
        pass
    return None


def is_tavily_configured() -> bool:
    key = get_tavily_api_key()
    return bool(key and key != "your_tavily_api_key_here")


def get_demo_research(destination: str) -> List[Dict[str, str]]:
    """
    Fallback demo data when Tavily API key is missing or service is temporarily unavailable.
    Clearly labeled so examiners/users know it's mock fallback data.
    """
    dest_clean = destination.strip().title() if destination else "Destination"
    return [
        {
            "title": f"[DEMO MODE] Top Attractions and Experiences in {dest_clean}",
            "url": f"https://en.wikipedia.org/wiki/{dest_clean.replace(' ', '_')}",
            "content": f"Popular travel guide highlights for {dest_clean}: iconic landmarks, heritage sites, scenic viewpoints, bustling local markets, and renowned cultural centers. (Note: Fallback simulated data used because Tavily API key was not supplied)."
        },
        {
            "title": f"[DEMO MODE] Best Dining, Cafes & Local Cuisine in {dest_clean}",
            "url": f"https://www.tripadvisor.in/Search?q={dest_clean.replace(' ', '+')}",
            "content": f"Gastronomic highlights of {dest_clean}: authentic regional delicacies, beachfront or rooftop cafes, bustling street food stalls, and highly rated local dining spots."
        },
        {
            "title": f"[DEMO MODE] Local Transit, Safety & Travel Practicalities in {dest_clean}",
            "url": f"https://wikitravel.org/en/{dest_clean.replace(' ', '_')}",
            "content": f"Getting around in {dest_clean}: reliable options include app-based cabs, local scooters/auto-rickshaws, and daytime public shuttles. Ideal visiting hours are early mornings and pleasant evenings."
        }
    ]


def tavily_search(query: str, destination: str = "", max_results: int = 4) -> List[Dict[str, str]]:
    """
    Search using Tavily API with graceful error handling and transparent fallback.
    Returns list of dicts: [{'title': '...', 'url': '...', 'content': '...'}]
    """
    api_key = get_tavily_api_key()
    if not is_tavily_configured():
        return get_demo_research(destination or query)

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=max_results,
            include_answer=False,
            include_raw_content=False,
        )
        results = []
        for item in response.get("results", []):
            results.append({
                "title": item.get("title", "Travel Resource"),
                "url": item.get("url", ""),
                "content": item.get("content", "").strip()
            })
        
        if not results:
            return get_demo_research(destination or query)
            
        return results
    except Exception as e:
        # Gracefully fall back rather than crashing workflow
        demo_results = get_demo_research(destination or query)
        demo_results[0]["title"] = f"[FALLBACK DUE TO ERROR: {str(e)[:30]}] {demo_results[0]['title']}"
        return demo_results
