"""
Destination Result Hero header showing dynamic Pexels imagery and trip overview stats.
"""
from typing import Dict, Any
import streamlit as st
from tools.image_search import search_travel_image


def render_destination_hero(state: Dict[str, Any]) -> None:
    """Render the post-generation destination hero banner with dynamic photography."""
    destination = state.get("destination", "Destination")
    duration = state.get("duration", 3)
    travellers = state.get("travellers", 2)
    budget_breakdown = state.get("budget_breakdown", {})
    validation = state.get("validation_result", {})
    trip_title = state.get("trip_title") or f"{destination} Getaway"
    trip_overview = state.get("trip_overview") or ""

    user_budget = float(state.get("budget", 0.0))
    total_cost = budget_breakdown.get("total", 0.0)
    is_valid = validation.get("is_valid", True)
    revisions = state.get("revision_count", 0)

    # Dynamic image lookup for destination
    query = f"{destination} landmark travel"
    img_data = search_travel_image(query=query, orientation="landscape", fallback_index=1)
    img_url = img_data.get("url", "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1200&q=80")
    photographer = img_data.get("photographer", "")

    badge_text = "✓ WITHIN BUDGET" if is_valid else (f"🔄 REVISED ({revisions}x)" if revisions > 0 else "⚠️ ADJUSTED")
    badge_bg = "rgba(16, 185, 129, 0.85)" if is_valid else "rgba(245, 158, 11, 0.85)"

    st.markdown(f"""
    <div class="dest-hero-card">
        <img class="dest-hero-bg" src="{img_url}" alt="{destination} scenery" loading="lazy" />
        <div class="dest-hero-overlay"></div>
        <div class="dest-hero-content">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem;">
                <span class="hero-tag" style="background:{badge_bg}; border:none;">
                    {badge_text}
                </span>
                {f'<span style="font-size:0.72rem; color:rgba(255,255,255,0.7);">Photo by {photographer}</span>' if photographer else ''}
            </div>
            <h1 style="font-size: 2.5rem; font-weight: 800; margin: 0.4rem 0 0.2rem 0; color: #FFFFFF; text-shadow: 0 2px 10px rgba(0,0,0,0.5);">
                {destination.upper()}
            </h1>
            <div style="font-size: 1.15rem; font-weight: 600; color: #E2E8F0; margin-bottom: 0.8rem;">
                "{trip_title}"
            </div>
            <div class="dest-chips-row">
                <span class="dest-chip">📅 {duration} Days</span>
                <span class="dest-chip">👥 {travellers} Travellers</span>
                <span class="dest-chip">💳 Target: ₹{user_budget:,.0f}</span>
                <span class="dest-chip">💰 Estimated: ₹{total_cost:,.0f}</span>
                <span class="dest-chip">🚗 From: {state.get('origin', 'Origin')}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if trip_overview:
        st.markdown(f"""
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 14px; padding: 1.1rem 1.4rem; margin-bottom: 1.8rem; font-size: 0.98rem; line-height: 1.6; color: #334155;">
            <b>Trip Overview:</b> {trip_overview}
        </div>
        """, unsafe_allow_html=True)
