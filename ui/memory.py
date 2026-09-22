"""
Profile and SQLite memory visualization for persisted travel preferences and trip history.
"""
from typing import Dict, Any, List
import streamlit as st
from memory.sqlite_memory import get_preferences, get_past_destinations


def render_memory_section(user_preferences: Dict[str, Any]) -> None:
    """Render the SQLite personalization profile and trip memory section."""
    db_prefs = get_preferences()
    past_dests = get_past_destinations(limit=5)

    # Use synthesized preferences from state if present, else SQLite database values
    prefs = user_preferences or db_prefs
    interests = prefs.get("interests", [])
    travel_style = prefs.get("travel_style", "balanced").capitalize()
    accom = prefs.get("accommodation_preference", "mid-range hotel").title()
    transit = prefs.get("transportation_preference", "flight").title()
    avoid = prefs.get("avoid", [])

    st.markdown("""
    <div style="margin-bottom: 1.4rem;">
        <h3 style="font-size: 1.35rem; font-weight: 800; color: #0F172A; margin-bottom: 0.2rem;">
            🧠 Your Travel Profile & Memory Persistence
        </h3>
        <p style="font-size: 0.88rem; color: #64748B;">
            Preferences and trip history stored across sessions in SQLite database (<code>data/travel_memory.db</code>).
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
        <div class="memory-stat-card">
            <div style="font-size: 0.85rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.6rem;">
                ❤️ Frequent & Active Interests
            </div>
        """, unsafe_allow_html=True)
        if interests:
            pills = "".join([f"<span class='memory-badge-pill'>{i}</span>" for i in interests])
            st.markdown(pills, unsafe_allow_html=True)
        else:
            st.write("No historical interests recorded yet.")
        st.markdown("</div>", unsafe_allow_html=True)

        if avoid:
            st.markdown("""
            <div class="memory-stat-card">
                <div style="font-size: 0.85rem; font-weight: 700; color: #991B1B; margin-bottom: 0.6rem;">
                    🚫 Learned Avoidances
                </div>
            """, unsafe_allow_html=True)
            avoid_pills = "".join([f"<span class='memory-badge-pill' style='background:#FEE2E2; color:#991B1B;'>{a}</span>" for a in avoid])
            st.markdown(avoid_pills, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="memory-stat-card">
            <div style="font-size: 0.85rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.6rem;">
                ⚙️ Baseline Travel Preferences
            </div>
            <div style="font-size: 0.88rem; line-height: 1.8; color: #334155;">
                <div>◷ <b>Default Pace:</b> {travel_style}</div>
                <div>🏨 <b>Preferred Stay:</b> {accom}</div>
                <div>🚗 <b>Preferred Transit:</b> {transit}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if past_dests:
            st.markdown("""
            <div class="memory-stat-card">
                <div style="font-size: 0.85rem; font-weight: 700; color: #0D9488; margin-bottom: 0.6rem;">
                    📍 Recent Trip History
                </div>
            """, unsafe_allow_html=True)
            dest_pills = "".join([f"<span class='memory-badge-pill' style='background:#CCFBF1; color:#0F766E;'>{d}</span>" for d in past_dests])
            st.markdown(dest_pills, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
