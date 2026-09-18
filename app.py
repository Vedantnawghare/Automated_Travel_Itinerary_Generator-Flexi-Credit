import os
import datetime
from typing import Dict, Any, List
import streamlit as st
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()

from agents.orchestrator import OrchestratorAgent
from tools.tavily_search import is_tavily_configured
from tools.n8n_webhook import send_to_n8n_webhook, get_n8n_webhook_url
from utils.llm_client import is_groq_configured, get_groq_model
from memory.sqlite_memory import get_preferences, initialize_db, get_past_destinations

# Streamlit Page Config
st.set_page_config(
    page_title="Automated Travel Itinerary Generator",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize local SQLite DB safely
initialize_db()

# Custom CSS for Travel Dashboard Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #0F172A;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .status-badge-pass {
        background-color: #DCFCE7;
        color: #166534;
        padding: 0.35rem 0.8rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .status-badge-revised {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 0.35rem 0.8rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .day-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .day-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1E40AF;
        margin-bottom: 0.5rem;
    }
    .time-slot-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #374151;
        margin-top: 0.5rem;
    }
    .agent-pill {
        display: inline-block;
        font-size: 0.75rem;
        background-color: #EEF2FF;
        color: #4338CA;
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        font-weight: 600;
        margin-right: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)


# Sidebar: Status & Past Memory
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=400&q=80", use_container_width=True)
    st.title("System Status")
    
    groq_ok = is_groq_configured()
    tavily_ok = is_tavily_configured()
    n8n_url = get_n8n_webhook_url()
    n8n_ok = bool(n8n_url and "your-n8n-instance" not in n8n_url)

    # Status indicators
    st.markdown("**API Integrations:**")
    st.write(f"🧠 **Groq LLM**: {'🟢 Configured (' + get_groq_model() + ')' if groq_ok else '🟡 Demo / Fallback Mode'}")
    st.write(f"🔍 **Tavily Search**: {'🟢 Active' if tavily_ok else '🟡 Simulated Demo Mode'}")
    st.write(f"⚡ **n8n Automation**: {'🟢 Configured' if n8n_ok else '⚪ URL Not Set'}")
    st.write("💾 **SQLite Memory**: 🟢 Connected (`data/travel_memory.db`)")

    if not groq_ok or not tavily_ok:
        st.info("💡 **Demo Mode Enabled**: Running with deterministic fallback algorithms & simulated research. Set `GROQ_API_KEY` and `TAVILY_API_KEY` in `.env` or Streamlit Cloud secrets to enable live models.")

    st.divider()
    st.subheader("Stored Memory")
    past_prefs = get_preferences()
    st.caption("Preferences retained in SQLite database:")
    if past_prefs.get("interests"):
        st.write(f"**Favorite Interests:** {', '.join(past_prefs['interests'][:4])}")
    st.write(f"**Default Pace:** {past_prefs.get('travel_style', 'balanced')}")
    st.write(f"**Preferred Stay:** {past_prefs.get('accommodation_preference', 'mid-range hotel')}")

    past_dests = get_past_destinations(limit=3)
    if past_dests:
        st.write(f"**Recent Trips:** {', '.join(past_dests)}")

    st.divider()
    st.caption("Agentic AI & Automation Project\nCourse Demonstration System")


# Header
st.markdown("<div class='main-header'>✈️ Automated Travel Itinerary Generator</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Autonomous Multi-Agent Travel Planning System powered by LangGraph, Groq, Tavily, SQLite & n8n</div>", unsafe_allow_html=True)

# Input Form in an Expander or Card
with st.container():
    st.subheader("Plan Your Trip")
    col1, col2, col3 = st.columns([1.2, 1.2, 1])

    with col1:
        destination = st.text_input("Destination", value="Goa", placeholder="e.g. Goa, Manali, Jaipur, Paris")
        origin = st.text_input("Starting City / Origin", value="Mumbai", placeholder="e.g. Mumbai, Delhi, Bengaluru")
        duration = st.number_input("Trip Duration (Days)", min_value=1, max_value=14, value=4, step=1)

    with col2:
        travellers = st.number_input("Number of Travellers", min_value=1, max_value=20, value=2, step=1)
        budget = st.number_input("Total Budget (₹ INR)", min_value=3000.0, max_value=1000000.0, value=32000.0, step=1000.0)
        travel_style = st.selectbox(
            "Travel Pace & Style",
            ["Relaxed", "Balanced", "Fast-Paced / Adventure", "Cultural / Immersive", "Luxury"],
            index=0
        )

    with col3:
        use_dates = st.checkbox("Specify exact travel dates", value=False)
        if use_dates:
            today = datetime.date.today()
            start_date_val = st.date_input("Departure Date", value=today + datetime.timedelta(days=14))
            end_date_val = start_date_val + datetime.timedelta(days=int(duration) - 1)
            st.caption(f"Trip Dates: {start_date_val} to {end_date_val}")
            start_date_str = start_date_val.isoformat()
            end_date_str = end_date_val.isoformat()
        else:
            start_date_str = None
            end_date_str = None
            st.caption("Dates omitted: Itinerary will generate as Day 1, Day 2, etc.")

        accommodation_pref = st.selectbox(
            "Accommodation Tier",
            ["Hostel / Backpacker", "Budget Hotel / Homestay", "Mid-Range Hotel", "Resort / Boutique", "Luxury Hotel"],
            index=2
        )
        transportation_pref = st.selectbox(
            "Transit Mode",
            ["Flight", "Train / Bus", "Road Trip / Cab", "Self-Drive"],
            index=0
        )

    # Interests and extra instructions
    interest_options = [
        "Beaches", "Cafes & Dining", "Nightlife & Pubs", "Heritage & Architecture",
        "Nature & Scenery", "Water Sports & Adventure", "Shopping & Bazaars",
        "Yoga & Wellness", "Local Street Food", "Photography"
    ]
    selected_interests = st.multiselect(
        "Interests & Activities (Select all that apply)",
        interest_options,
        default=["Beaches", "Cafes & Dining", "Nightlife & Pubs"]
    )

    col_extra1, col_extra2 = st.columns([2, 1])
    with col_extra1:
        extra_instructions = st.text_input("Special Requests / Avoidances", value="Avoid overly crowded commercial spots, prefer scenic seaside cafes")
    with col_extra2:
        user_email = st.text_input("Email (for n8n calendar/itinerary dispatch)", value="traveler@example.com")

    generate_btn = st.button("🚀 Generate My Itinerary", type="primary", use_container_width=True)


# Processing logic
if generate_btn:
    user_payload = {
        "destination": destination,
        "origin": origin,
        "start_date": start_date_str,
        "end_date": end_date_str,
        "duration": duration,
        "travellers": travellers,
        "budget": budget,
        "currency": "INR",
        "currency_symbol": "₹",
        "interests": selected_interests,
        "travel_style": travel_style.lower(),
        "accommodation_preference": accommodation_pref.lower(),
        "transportation_preference": transportation_pref.lower(),
        "extra_instructions": extra_instructions,
        "email": user_email,
        "user_key": "default_user",
    }

    with st.spinner("🤖 Orchestrating Multi-Agent Workflow (Planner -> Researcher -> Preference -> Budget -> Itinerary -> Validator)..."):
        orchestrator = OrchestratorAgent()
        result_state = orchestrator.plan_trip(user_payload)
        st.session_state["trip_result"] = result_state


# Display results if available in session state
if "trip_result" in st.session_state:
    state = st.session_state["trip_result"]
    final = state.get("final_response", {})
    budget_breakdown = state.get("budget_breakdown", {})
    itinerary = state.get("itinerary", [])
    validation = state.get("validation_result", {})
    research = state.get("research_results", [])
    trace = state.get("execution_trace", [])
    preferences_used = state.get("preferences", {})

    st.markdown("---")

    # Top Status & Metrics Bar
    st.subheader("Trip Overview & Financial Feasibility")
    m1, m2, m3, m4, m5 = st.columns(5)

    tot_cost = budget_breakdown.get("total", 0.0)
    user_bud = float(state.get("budget", 0.0))
    rem_bud = budget_breakdown.get("remaining", user_bud - tot_cost)
    within_bud = budget_breakdown.get("within_budget", tot_cost <= user_bud)

    with m1:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Destination</div><div class='metric-value'>{state.get('destination')}</div></div>", unsafe_allow_html=True)
    with m2:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Total Cost</div><div class='metric-value'>₹{tot_cost:,.0f}</div></div>", unsafe_allow_html=True)
    with m3:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Your Budget</div><div class='metric-value'>₹{user_bud:,.0f}</div></div>", unsafe_allow_html=True)
    with m4:
        diff_color = "#166534" if rem_bud >= 0 else "#991B1B"
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Remaining Buffer</div><div class='metric-value' style='color:{diff_color};'>₹{rem_bud:,.0f}</div></div>", unsafe_allow_html=True)
    with m5:
        badge_class = "status-badge-pass" if validation.get("is_valid") else "status-badge-revised"
        status_label = "VALIDATED" if validation.get("is_valid") else f"REVISED ({state.get('revision_count', 0)}x)"
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Validation Status</div><div style='margin-top:0.3rem;'><span class='{badge_class}'>{status_label}</span></div></div>", unsafe_allow_html=True)

    # Multi-Agent Workflow Execution Stepper / Trace
    with st.expander("🔍 Multi-Agent Execution Trace & Agentic Reasoning Log", expanded=False):
        st.write("Real-time trace generated by LangGraph state machine:")
        for step in trace:
            status_icon = "🟢" if step.get("status") == "completed" else ("🔵" if step.get("status") == "started" else "🟡")
            st.markdown(f"{status_icon} <span class='agent-pill'>{step.get('agent')}</span> {step.get('action')} *(at {step.get('timestamp')})*", unsafe_allow_html=True)

        if state.get("revision_count", 0) > 0:
            st.info(f"🔄 **Self-Correction Triggered**: Validation Agent flagged issues on initial pass; Orchestrator routed back through Revision Agent to optimize constraints (Revisions: {state.get('revision_count')}).")

    # Two column layout: Budget breakdown and Day-wise Itinerary
    tab_itinerary, tab_budget, tab_research, tab_memory = st.tabs(["📅 Day-by-Day Itinerary", "💰 Itemized Budget", "🌐 Live Web Research", "🧠 Stored Memory & Preferences"])

    with tab_itinerary:
        trip_title = state.get("trip_title") or f"Curated Itinerary for {state.get('destination')}"
        trip_overview = state.get("trip_overview") or "Detailed day-wise travel schedule tailored to your interests."
        st.markdown(f"### {trip_title}")
        st.write(trip_overview)

        for day in itinerary:
            day_num = day.get("day", 1)
            day_date = day.get("date")
            date_display = f" — {day_date}" if day_date else ""
            theme = day.get("theme", f"Day {day_num} Exploration")
            day_cost = day.get("estimated_cost", 0)

            with st.container():
                st.markdown(f"""
                <div class='day-card'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <div class='day-title'>Day {day_num}{date_display}: {theme}</div>
                        <div style='font-weight:600; color:#047857;'>Est. Spend: ₹{day_cost:,.0f}</div>
                    </div>
                """, unsafe_allow_html=True)

                col_m, col_a, col_e = st.columns(3)
                with col_m:
                    st.markdown("<div class='time-slot-title'>🌅 Morning</div>", unsafe_allow_html=True)
                    for act in day.get("morning", []):
                        st.markdown(f"- {act}")
                with col_a:
                    st.markdown("<div class='time-slot-title'>☀️ Afternoon</div>", unsafe_allow_html=True)
                    for act in day.get("afternoon", []):
                        st.markdown(f"- {act}")
                with col_e:
                    st.markdown("<div class='time-slot-title'>🌙 Evening & Night</div>", unsafe_allow_html=True)
                    for act in day.get("evening", []):
                        st.markdown(f"- {act}")

                if day.get("notes") or day.get("travel_tips"):
                    st.caption(f"📌 **Tips & Logistics:** {day.get('notes', '')} {day.get('travel_tips', '')}")

                st.markdown("</div>", unsafe_allow_html=True)

    with tab_budget:
        st.subheader("Deterministic Cost Allocation (INR)")
        st.write("Numerical costs are deterministically calculated by the Budget Agent (not hallucinated by LLM arithmetic).")

        b_col1, b_col2 = st.columns([1, 1])
        with b_col1:
            budget_data = {
                "Category": [
                    "Intercity Transit (Round Trip)",
                    "Accommodation",
                    "Dining & Food",
                    "Activities & Entry Fees",
                    "Local Transportation",
                    "Buffer / Miscellaneous (6%)",
                    "Total Estimated Spend",
                    "User Budget",
                    "Remaining Buffer"
                ],
                "Amount (₹)": [
                    f"₹{budget_breakdown.get('transportation', 0):,.0f}",
                    f"₹{budget_breakdown.get('accommodation', 0):,.0f}",
                    f"₹{budget_breakdown.get('food', 0):,.0f}",
                    f"₹{budget_breakdown.get('activities', 0):,.0f}",
                    f"₹{budget_breakdown.get('local_transport', 0):,.0f}",
                    f"₹{budget_breakdown.get('miscellaneous', 0):,.0f}",
                    f"₹{budget_breakdown.get('total', 0):,.0f}",
                    f"₹{user_bud:,.0f}",
                    f"₹{rem_bud:,.0f}",
                ]
            }
            st.table(budget_data)

        with b_col2:
            st.write("**Budget Breakdown Logic:**")
            for note in budget_breakdown.get("breakdown_notes", []):
                st.write(f"- {note}")

    with tab_research:
        st.subheader("Web Research Findings (Tavily Tool)")
        if not research:
            st.info("No research items recorded.")
        else:
            for item in research:
                st.markdown(f"**[{item.get('title', 'Source')}]({item.get('url', '#')})**")
                st.write(item.get("content", ""))
                st.caption(f"Source URL: {item.get('url', 'N/A')}")
                st.divider()

    with tab_memory:
        st.subheader("Synthesized Preference Profile & SQLite Memory")
        st.json(preferences_used)

    # Action Bar: Regenerate and n8n Automate
    st.divider()
    st.subheader("Automation & Export Actions")
    act_col1, act_col2 = st.columns([1, 1])

    with act_col1:
        if st.button("🔄 Regenerate / Rerun Workflow", use_container_width=True):
            st.rerun()

    with act_col2:
        n8n_button = st.button("⚡ Dispatch to n8n Webhook (Google Calendar + Gmail)", type="primary", use_container_width=True)
        if n8n_button:
            webhook_payload = {
                "destination": state.get("destination"),
                "origin": state.get("origin"),
                "start_date": state.get("start_date"),
                "end_date": state.get("end_date"),
                "duration": state.get("duration"),
                "travellers": state.get("travellers"),
                "budget": state.get("budget"),
                "total_estimated_cost": budget_breakdown.get("total"),
                "currency": "INR",
                "preferences": preferences_used,
                "itinerary": itinerary,
                "email": state.get("email"),
                "create_calendar_events": True,
                "send_email": True,
            }
            res = send_to_n8n_webhook(webhook_payload)
            if res.get("success"):
                st.success(f"✅ {res.get('message')}")
            else:
                st.warning(f"⚠️ {res.get('message')}")
