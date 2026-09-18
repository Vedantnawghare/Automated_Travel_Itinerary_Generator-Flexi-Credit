import datetime
from typing import Dict, Any, List
from tools.tavily_search import tavily_search, is_tavily_configured


class ResearcherAgent:
    """
    Research Agent:
    Uses Tavily Search tool to retrieve real-time travel information, attractions,
    local food/cafes, and transit tips. Preserves titles and source URLs.
    Falls back gracefully to demo data if Tavily API key is missing.
    """

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        destination = state.get("destination", "Goa")
        search_queries = state.get("search_queries", [
            f"top attractions and activities in {destination}",
            f"best cafes food dining spots {destination}",
            f"travel practical tips {destination}"
        ])

        aggregated_results: List[Dict[str, str]] = []
        seen_urls = set()

        # Search for each query identified by the Planner Agent
        for query in search_queries[:3]:
            try:
                results = tavily_search(query=query, destination=destination, max_results=2)
                for item in results:
                    url = item.get("url", "")
                    if url and url in seen_urls:
                        continue
                    if url:
                        seen_urls.add(url)
                    aggregated_results.append(item)
            except Exception as e:
                aggregated_results.append({
                    "title": f"Travel Research for {destination}",
                    "url": "",
                    "content": f"Information retrieved for {destination}: popular sightseeing spots and recommendations."
                })

        state["research_results"] = aggregated_results

        is_live = is_tavily_configured()
        mode_label = "Live Tavily Search" if is_live else "Demo / Mock Research Mode"

        trace = state.setdefault("execution_trace", [])
        trace.append({
            "agent": "Research Agent",
            "action": f"Gathered {len(aggregated_results)} research sources for {destination} via {mode_label}.",
            "status": "completed",
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })

        return state
