"""
Modern, grouped travel input form layout.
Organizes inputs into clean visual cards: WHERE, WHEN, WHO & BUDGET, STYLE & COMFORT, INTERESTS.
"""
import datetime
from typing import Dict, Any, Tuple
import streamlit as st


def render_trip_input_form() -> Tuple[Dict[str, Any], bool]:
    """
    Render grouped travel planning form with polished UI styling.
    Returns: (user_payload_dict, generate_button_clicked)
    """
    st.markdown("""
    <div style="margin-bottom: 1.2rem;">
        <h2 style="font-size: 1.5rem; font-weight: 800; color: #0F172A; margin-bottom: 0.2rem;">
            🗺️ Configure Your Travel Request
        </h2>
        <p style="font-size: 0.95rem; color: #64748B;">
            Customize your destination, timeline, budget limits, and style preferences.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Group 1: Where & When (2 columns)
    col_where, col_when = st.columns(2)

    with col_where:
        st.markdown("""
        <div class="form-section-header">
            <span class="form-icon-pill">📍</span>
            <span>Where are you heading?</span>
        </div>
        """, unsafe_allow_html=True)
        destination = st.text_input(
            "Destination",
            value="Goa",
            placeholder="e.g. Goa, Jaipur, Manali, Paris, Tokyo",
            help="Primary travel destination or city to explore."
        )
        origin = st.text_input(
            "Starting City / Origin",
            value="Mumbai",
            placeholder="e.g. Mumbai, Delhi, Bengaluru, London",
            help="Departure location for intercity travel calculations."
        )

    with col_when:
        st.markdown("""
        <div class="form-section-header">
            <span class="form-icon-pill">📅</span>
            <span>Trip Timeline & Duration</span>
        </div>
        """, unsafe_allow_html=True)
        duration = st.number_input(
            "Trip Duration (Days)",
            min_value=1,
            max_value=14,
            value=4,
            step=1,
            help="Total number of travel days."
        )
        use_dates = st.checkbox("Specify exact travel dates", value=False)
        if use_dates:
            today = datetime.date.today()
            start_date_val = st.date_input("Departure Date", value=today + datetime.timedelta(days=14))
            end_date_val = start_date_val + datetime.timedelta(days=int(duration) - 1)
            st.caption(f"🗓️ {start_date_val.strftime('%b %d, %Y')} → {end_date_val.strftime('%b %d, %Y')} ({duration} days)")
            start_date_str = start_date_val.isoformat()
            end_date_str = end_date_val.isoformat()
        else:
            start_date_str = None
            end_date_str = None
            st.caption("Duration-only mode: Itinerary generates as Day 1, Day 2, etc.")

    # Group 2: Who & Budget
    col_who, col_budget = st.columns(2)

    with col_who:
        st.markdown("""
        <div class="form-section-header">
            <span class="form-icon-pill">👥</span>
            <span>Who is Traveling?</span>
        </div>
        """, unsafe_allow_html=True)
        travellers = st.number_input(
            "Number of Travellers",
            min_value=1,
            max_value=20,
            value=2,
            step=1,
            help="Group size used for lodging and transit cost allocations."
        )

    with col_budget:
        st.markdown("""
        <div class="form-section-header">
            <span class="form-icon-pill">💳</span>
            <span>Total Travel Budget</span>
        </div>
        """, unsafe_allow_html=True)
        budget = st.number_input(
            "Target Budget (₹ INR)",
            min_value=3000.0,
            max_value=2000000.0,
            value=32000.0,
            step=1000.0,
            help="Total budget for group. Validator Agent checks feasibility against this ceiling."
        )

    # Group 3: Style & Comfort
    col_pace, col_stay, col_trans = st.columns(3)

    with col_pace:
        st.markdown("""
        <div class="form-section-header">
            <span class="form-icon-pill">⚡</span>
            <span>Travel Pace</span>
        </div>
        """, unsafe_allow_html=True)
        travel_style = st.selectbox(
            "Pace & Vibe",
            ["Relaxed", "Balanced", "Fast-Paced / Adventure", "Cultural / Immersive", "Luxury"],
            index=0
        )

    with col_stay:
        st.markdown("""
        <div class="form-section-header">
            <span class="form-icon-pill">🏨</span>
            <span>Lodging Tier</span>
        </div>
        """, unsafe_allow_html=True)
        accommodation_pref = st.selectbox(
            "Accommodation Type",
            ["Hostel / Backpacker", "Budget Hotel / Homestay", "Mid-Range Hotel", "Resort / Boutique", "Luxury Hotel"],
            index=2
        )

    with col_trans:
        st.markdown("""
        <div class="form-section-header">
            <span class="form-icon-pill">🚗</span>
            <span>Intercity Transit</span>
        </div>
        """, unsafe_allow_html=True)
        transportation_pref = st.selectbox(
            "Transit Mode",
            ["Flight", "Train / Bus", "Road Trip / Cab", "Self-Drive"],
            index=0
        )

    # Group 4: Interests & Custom Requests
    st.markdown("""
    <div class="form-section-header" style="margin-top: 0.8rem;">
        <span class="form-icon-pill">🎯</span>
        <span>Interests, Activities & Special Requests</span>
    </div>
    """, unsafe_allow_html=True)

    interest_options = [
        "Beaches", "Cafes & Dining", "Nightlife & Pubs", "Heritage & Architecture",
        "Nature & Scenery", "Water Sports & Adventure", "Shopping & Bazaars",
        "Yoga & Wellness", "Local Street Food", "Photography"
    ]

    selected_interests = st.multiselect(
        "Select Interests & Activities",
        interest_options,
        default=["Beaches", "Cafes & Dining", "Nightlife & Pubs"],
        help="Planner and Itinerary agents prioritize activities matching your interests."
    )

    col_notes, col_email = st.columns([2, 1])
    with col_notes:
        extra_instructions = st.text_input(
            "Special Requests / Dislikes / Avoidances",
            value="Avoid overly crowded commercial spots, prefer scenic seaside cafes",
            help="Directives and constraints passed to Preference and Validation agents."
        )
    with col_email:
        user_email = st.text_input(
            "Recipient Email (for n8n Automation)",
            value="traveler@example.com",
            help="Email used when triggering the automated n8n calendar & itinerary webhook."
        )

    # Primary Action Button
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    generate_btn = st.button(
        "✨ Generate My Personalized Trip",
        type="primary",
        use_container_width=True
    )

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

    return user_payload, generate_btn
