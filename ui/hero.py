"""
Cinematic travel hero banner with dynamic visual backdrop and gradient overlays.
"""
import streamlit as st
from tools.image_search import search_travel_image


def render_hero(destination: str = "Wanderlust Travel") -> None:
    """Render cinematic travel hero banner."""
    # Retrieve dynamic travel image for current destination or generic landscape
    query = f"{destination} landscape scenic travel" if destination else "panoramic travel destination"
    img_data = search_travel_image(query=query, orientation="landscape", fallback_index=0)
    img_url = img_data.get("url", "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=1200&q=80")

    st.markdown(f"""
    <div class="travel-hero">
        <img class="hero-bg-img" src="{img_url}" alt="Travel destination panoramic view" loading="lazy" />
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <span class="hero-tag">✨ Autonomous Agentic Travel Planner</span>
            <h1 class="hero-title">Plan Your Perfect Journey</h1>
            <p class="hero-subtitle">
                Decomposes travel goals, conducts real-time web research, optimizes budgets deterministically,
                and self-corrects schedules using a collaborative multi-agent architecture.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
