import os
import datetime
from typing import Dict, Any, List
import streamlit as st
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()

from agents.orchestrator import OrchestratorAgent
from memory.sqlite_memory import get_preferences, initialize_db, get_past_destinations
from tools.image_search import search_travel_image

# Modular UI Presentation Layer
from ui.theme import inject_custom_theme
from ui.nav import render_navbar, render_sidebar_status
from ui.hero import render_hero
from ui.forms import render_trip_input_form
from ui.destination import render_destination_hero
from ui.itinerary import render_itinerary_cards
from ui.budget import render_budget_section
from ui.agent_trace import render_agent_pipeline_visual
from ui.research import render_research_sources
from ui.memory import render_memory_section
from ui.automation import render_automation_panel

# 1. Streamlit Page Configuration
st.set_page_config(
    page_title="TravelAI — Automated Travel Itinerary Generator",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Initialize local SQLite DB safely
initialize_db()

# 3. Inject CSS Theme, Glassmorphic Surfaces & Animations
inject_custom_theme()

# 4. Sidebar: Integrations, Stored Profile & Quick Stats
with st.sidebar:
    sidebar_img = search_travel_image(query="tropical wanderlust journey travel", fallback_index=2)
    st.image(sidebar_img.get("url"), use_container_width=True)

    render_sidebar_status()

    st.divider()
    st.subheader("💾 Stored Preferences")
    past_prefs = get_preferences()
    st.caption("Active traveler profile in SQLite database:")
    if past_prefs.get("interests"):
        st.write(f"❤️ **Interests:** {', '.join(past_prefs['interests'][:3])}")
    st.write(f"◷ **Pace:** {past_prefs.get('travel_style', 'balanced').capitalize()}")
    st.write(f"🏨 **Lodging:** {past_prefs.get('accommodation_preference', 'mid-range hotel').title()}")

    past_dests = get_past_destinations(limit=3)
    if past_dests:
        st.write(f"📍 **Recent Trips:** {', '.join(past_dests)}")

    st.divider()
    st.caption("TravelAI Multi-Agent System\nPowered by LangGraph, Groq, Tavily, Pexels & SQLite")

# 5. Top Brand Navigation Bar
render_navbar()

# 6. Hero Banner (shows selected destination or dynamic travel imagery)
current_dest = st.session_state.get("current_destination", "Goa")
render_hero(destination=current_dest)

# 7. Travel Request Input Form
user_payload, generate_btn = render_trip_input_form()

# Update stored destination for hero imagery
if user_payload.get("destination"):
    st.session_state["current_destination"] = user_payload["destination"]

# 8. Generation Processing
if generate_btn:
    with st.spinner("🤖 Orchestrating Multi-Agent Workflow (Planner ➔ Researcher ➔ Preferences ➔ Budget ➔ Builder ➔ Validator)..."):
        orchestrator = OrchestratorAgent()
        result_state = orchestrator.plan_trip(user_payload)
        st.session_state["trip_result"] = result_state

# 9. Display Visual Results
if "trip_result" in st.session_state:
    state = st.session_state["trip_result"]
    budget_breakdown = state.get("budget_breakdown", {})
    itinerary = state.get("itinerary", [])
    validation = state.get("validation_result", {})
    research = state.get("research_results", [])
    trace = state.get("execution_trace", [])
    preferences_used = state.get("preferences", {})

    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

    # Post-generation destination hero with dynamic photo
    render_destination_hero(state)

    # Agentic Workflow Execution Stepper
    render_agent_pipeline_visual(trace, state.get("revision_count", 0))

    # Structured Output Tabs
    tab_itinerary, tab_budget, tab_research, tab_memory = st.tabs([
        "📅 Day-by-Day Itinerary",
        "💰 Itemized Budget",
        "🌐 Live Web Research",
        "🧠 Stored Memory & Profile"
    ])

    with tab_itinerary:
        render_itinerary_cards(itinerary, state.get("destination", "Destination"))

    with tab_budget:
        render_budget_section(budget_breakdown, float(state.get("budget", 0.0)))

    with tab_research:
        render_research_sources(research)

    with tab_memory:
        render_memory_section(preferences_used)

    # External Workflow Action Panel (n8n Webhook & Reset)
    render_automation_panel(state)
