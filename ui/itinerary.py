"""
Interactive Day-by-Day travel cards with dynamic Pexels place imagery,
3D hover lift, time slots (Morning, Afternoon, Evening), and day-spend chips.
"""
from typing import Dict, Any, List
import streamlit as st
from tools.image_search import search_travel_image, extract_search_query_for_day


def render_itinerary_cards(itinerary: List[Dict[str, Any]], destination: str) -> None:
    """Render structured visual itinerary cards with dynamic imagery."""
    if not itinerary:
        st.info("No itinerary days generated.")
        return

    st.markdown("""
    <div style="margin-bottom: 1.4rem;">
        <h3 style="font-size: 1.35rem; font-weight: 800; color: #0F172A; margin-bottom: 0.2rem;">
            📅 Day-by-Day Curated Schedule
        </h3>
        <p style="font-size: 0.88rem; color: #64748B;">
            Intelligently sequenced by geographic proximity, travel style, and activity pacing.
        </p>
    </div>
    """, unsafe_allow_html=True)

    for idx, day in enumerate(itinerary):
        day_num = day.get("day", idx + 1)
        day_date = day.get("date")
        date_display = f" • {day_date}" if day_date else ""
        theme = day.get("theme", f"Day {day_num} Exploration")
        day_cost = float(day.get("estimated_cost", 0))

        morning_acts = day.get("morning", [])
        afternoon_acts = day.get("afternoon", [])
        evening_acts = day.get("evening", [])
        notes = day.get("notes", "")
        travel_tips = day.get("travel_tips", "")

        # Extract dynamic place image query derived from the day's specific activities & destination
        day_query = extract_search_query_for_day(destination, day)
        img_data = search_travel_image(query=day_query, orientation="landscape", fallback_index=idx % 5)
        img_url = img_data.get("url", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80")
        photographer = img_data.get("photographer", "")

        # Render Day Card
        st.markdown(f"""
        <div class="day-travel-card">
            <div class="day-banner-container">
                <img class="day-banner-img" src="{img_url}" alt="{day_query}" loading="lazy" />
                <div class="day-banner-overlay">
                    <div>
                        <span style="font-size: 0.76rem; font-weight: 700; color: #93C5FD; text-transform: uppercase; letter-spacing: 0.06em;">
                            {destination.upper()} • {day_query.title()}
                        </span>
                        <div class="day-badge-title">Day {day_num}{date_display}</div>
                        <div style="font-size: 0.95rem; color: #F1F5F9; font-weight: 500;">{theme}</div>
                    </div>
                    <div style="text-align: right;">
                        <span class="day-cost-tag">Est. Spend: ₹{day_cost:,.0f}</span>
                        {f'<div style="font-size: 0.65rem; color: rgba(255,255,255,0.7); margin-top: 0.2rem;">Photo: {photographer}</div>' if photographer else ''}
                    </div>
                </div>
            </div>
            <div class="day-card-body">
        """, unsafe_allow_html=True)

        # Time Slots Grid (Morning, Afternoon, Evening)
        slot_col1, slot_col2, slot_col3 = st.columns(3)

        with slot_col1:
            st.markdown("""
            <div class="time-slot-card">
                <div class="time-slot-header">🌅 Morning</div>
            """, unsafe_allow_html=True)
            for act in morning_acts:
                st.markdown(f"<div class='activity-bullet'>{act}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with slot_col2:
            st.markdown("""
            <div class="time-slot-card">
                <div class="time-slot-header">☀️ Afternoon</div>
            """, unsafe_allow_html=True)
            for act in afternoon_acts:
                st.markdown(f"<div class='activity-bullet'>{act}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with slot_col3:
            st.markdown("""
            <div class="time-slot-card">
                <div class="time-slot-header">🌙 Evening & Night</div>
            """, unsafe_allow_html=True)
            for act in evening_acts:
                st.markdown(f"<div class='activity-bullet'>{act}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Tips & Logistics Bar
        if notes or travel_tips:
            tips_text = f"{notes} {travel_tips}".strip()
            st.markdown(f"""
            <div class="day-tips-box">
                <b>💡 Tips & Logistics:</b> {tips_text}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)
